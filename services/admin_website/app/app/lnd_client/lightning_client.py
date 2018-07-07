import codecs
import os
from sys import platform
from typing import List

import grpc
from grpc._plugin_wrapping import (
    _AuthMetadataPluginCallback,
    _AuthMetadataContext
)

import app.lnd_client.grpc_generated.rpc_pb2 as ln
import app.lnd_client.grpc_generated.rpc_pb2_grpc as lnrpc

# Due to updated ECDSA generated tls.cert we need to let gprc know that
# we need to use that cipher suite otherwise there will be a handshake
# error when we communicate with the lnd rpc server.
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'


class LightningClient(object):
    def __init__(self, rpc_uri: str, peer_uri: str, name: str = None):
        self.name = name
        self.peer_uri = peer_uri

        if os.environ.get('LND_AUTH_DATA_PATH'):
            path = os.environ.get('LND_AUTH_DATA_PATH')
        elif platform == "linux" or platform == "linux2":
            path = '~/.lnd/'
        elif platform == "darwin":
            path = '~/Library/Application Support/Lnd/'
        else:
            raise Exception(f"What's the {platform} path for the lnd tls cert?")
        self.main_lnd_path = os.path.expanduser(path)

        if name is None:
            self.data_path = self.main_lnd_path
        else:
            data_path = os.path.expanduser(f'~/go/dev/{name}/data')
            if not os.path.exists(data_path):
                raise Exception(f'Invalid path {data_path}')
            self.data_path = data_path

        lnd_tls_cert_path = os.path.join(self.main_lnd_path, 'tls.cert')
        self.lnd_tls_cert = open(lnd_tls_cert_path, 'rb').read()

        cert_credentials = grpc.ssl_channel_credentials(self.lnd_tls_cert)

        admin_macaroon_path = os.path.join(self.data_path, 'admin.macaroon')
        with open(admin_macaroon_path, 'rb') as f:
            macaroon_bytes = f.read()
            self.macaroon = codecs.encode(macaroon_bytes, 'hex')

        def metadata_callback(context: _AuthMetadataPluginCallback,
                              callback: _AuthMetadataContext):
            callback([('macaroon', self.macaroon)], None)

        auth_credentials = grpc.metadata_call_credentials(metadata_callback)

        self.credentials = grpc.composite_channel_credentials(cert_credentials,
                                                              auth_credentials)

        self.grpc_channel = grpc.secure_channel(rpc_uri,
                                                self.credentials

                                                  )
        self.lnd_client = lnrpc.LightningStub(self.grpc_channel)

    def get_info(self) -> ln.GetInfoResponse:
        return self.lnd_client.GetInfo(ln.GetInfoRequest())

    @property
    def pubkey(self):
        return self.get_info().identity_pubkey

    def get_wallet_balance(self) -> ln.WalletBalanceResponse:
        return self.lnd_client.WalletBalance(ln.WalletBalanceRequest())

    def get_transactions(self) -> List[ln.Transaction]:
        request = ln.GetTransactionsRequest()
        response = self.lnd_client.GetTransactions(request)
        return response.transactions

    def get_channel_balance(self) -> ln.ChannelBalanceResponse:
        request = ln.ChannelBalanceRequest()
        response = self.lnd_client.ChannelBalance(request)
        return response

    def get_channels(self) -> List[ln.Channel]:
        return self.lnd_client.ListChannels(ln.ListChannelsRequest()).channels

    def get_invoices(self, pending_only: bool = False) -> List[ln.Invoice]:
        request = ln.ListInvoiceRequest(pending_only=pending_only)
        response = self.lnd_client.ListInvoices(request)
        return response.invoices

    def get_payments(self) -> List[ln.Payment]:
        request = ln.ListPaymentsRequest()
        response = self.lnd_client.ListPayments(request)
        return response.payments

    def get_new_address(self, address_type: str = 'p2wkh') -> str:
        request = ln.NewAddressRequest(type=address_type)
        response = self.lnd_client.NewAddress(request)
        return response.address

    def get_peers(self) -> ln.ListPeersResponse:
        return self.lnd_client.ListPeers(ln.ListPeersRequest()).peers

    def connect_peer(self, pubkey: str, host: str) -> ln.ConnectPeerResponse:
        address = ln.LightningAddress(pubkey=pubkey, host=host)
        request = ln.ConnectPeerRequest(addr=address)
        response = self.lnd_client.ConnectPeer(request)
        return response

    def disconnect_peer(self, pub_key: str) -> ln.DisconnectPeerResponse:
        request = ln.DisconnectPeerRequest(pub_key=pub_key)
        response = self.lnd_client.DisconnectPeer(request)
        return response

    def open_channel(self, **kwargs):
        kwargs['node_pubkey'] = codecs.decode(kwargs['node_pubkey_string'], 'hex')
        request = ln.OpenChannelRequest(**kwargs)
        response = self.lnd_client.OpenChannel(request)
        return response

    def open_channel_sync(self, **kwargs):
        kwargs['node_pubkey'] = codecs.decode(kwargs['node_pubkey_string'], 'hex')
        request = ln.OpenChannelRequest(**kwargs)
        response = self.lnd_client.OpenChannelSync(request)
        return response

    def create_invoice(self, **kwargs) -> ln.AddInvoiceResponse:
        request = ln.Invoice(**kwargs)
        return self.lnd_client.AddInvoice(request)

    @staticmethod
    def request_generator(**kwargs):
        yield ln.SendRequest(**kwargs)

    def send_payment(self, **kwargs) -> ln.SendResponse:
        request_iterable = self.request_generator(**kwargs)
        response = self.lnd_client.SendPayment(request_iterable)
        return response

    def decode_payment_request(self, pay_req: str) -> ln.PayReq:
        request = ln.PayReqString(pay_req=pay_req)
        response = self.lnd_client.DecodePayReq(request)
        return response

    def send_payment_sync(self, **kwargs) -> ln.SendResponse:
        request = ln.SendRequest(**kwargs)
        response = self.lnd_client.SendPaymentSync(request)
        return response

    def close_channel(self, channel_point: str):
        request = ln.CloseChannelRequest(channel_point=channel_point)
        response = self.lnd_client.CloseChannel(request)
        return response
