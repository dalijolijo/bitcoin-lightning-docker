import os
from pprint import pformat

import bitcoin.rpc
from flask import Flask, redirect
from flask_admin import Admin, AdminIndexView, expose, BaseView
from google.protobuf.json_format import MessageToDict
from markupsafe import Markup

from app.lnd_client.admin.channels import ChannelModelView
from app.lnd_client.grpc_generated.rpc_pb2 import Channel
from app.lnd_client.lightning_client import LightningClient

if os.environ.get('TESTNET', 1):
    bitcoin.SelectParams('testnet')

class BlockchainView(AdminIndexView):
    @expose('/')
    def index(self):
        proxy = bitcoin.rpc.Proxy(btc_conf_file='bitcoin.conf')

        try:
            blockchain_info = proxy.call('getblockchaininfo')
        except Exception as exc:
            blockchain_info = {'Error': str(exc)}

        try:
            mempool_info = proxy.call('getmempoolinfo')
        except Exception as exc:
            mempool_info = {'Error': str(exc)}

        try:
            wallet_info = proxy.call('getwalletinfo')
        except Exception as exc:
            wallet_info = {'Error': str(exc)}


        try:
            new_address = {
                'bech32': proxy.call('getnewaddress', '', 'bech32'),
                'p2sh-segwit': proxy.call('getnewaddress', '', 'p2sh-segwit'),
                'legacy': proxy.call('getnewaddress', '', 'legacy'),
            }
            if blockchain_info['chain'] == 'test':
                testnet_faucet = 'https://testnet.coinfaucet.eu/'
                new_address['Get testnet coins'] = Markup(f'<a target="_blank" href="{testnet_faucet}">{testnet_faucet}</a>')
        except Exception as exc:
            new_address = {'Error': str(exc)}

        websocket_port = os.environ.get('WEBSOCKET_PORT', 8765)
        return self.render('admin/bitcoind_home.html',
                           websocket_port=websocket_port,
                           blockchain_info=blockchain_info,
                           mempool_info=mempool_info,
                           wallet_info=wallet_info,
                           new_address=new_address
                           )

class LightningView(BaseView):
    @expose('/')
    def index(self):
        rpc_uri = os.environ.get('LND_RPC_URI', '127.0.0.1:10009')
        peer_uri = os.environ.get('LND_PEER_URI', '127.0.0.1:9735')
        ln = LightningClient(rpc_uri=rpc_uri, peer_uri=peer_uri)

        try:
            lnd_info = ln.get_info()
            lnd_info = MessageToDict(lnd_info)
        except Exception as exc:
            lnd_info = {'Error': ' '.join([str(type(exc)), str(exc)])}


        try:
            peers = ln.get_peers()
            peers = MessageToDict(peers)['peers']
            if not peers:
                peers = {'No peers': ' '}
        except Exception as exc:
            peers = {'Error': ' '.join([str(type(exc)), str(exc)])}

        try:
            channels = ln.get_channels()
            channels = MessageToDict(channels)['channels']
            if not channels:
                channels = {'No channels': ' '}
        except Exception as exc:
            channels = {'Error': ' '.join([str(type(exc)), str(exc)])}

        return self.render('admin/lnd_home.html',
                           lnd_info=lnd_info,
                           peers=peers,
                           channels=channels)

def create_app():
    app = Flask(__name__)
    app.debug = True
    admin = Admin(app=app,
                  name='Bitcoin/LN',
                  template_mode='bootstrap3',
                  index_view=BlockchainView(name='Bitcoin')
                  )
    app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
    @app.route('/')
    def index():
        return redirect('/admin')

    admin.add_view(LightningView(name='Lightning', endpoint='lightning'))

    admin.add_view(ChannelModelView(Channel))

    with open('bitcoin.conf', 'w') as conf_file:
        lines = [
            ('rpcconnect', os.environ.get('BITCOIND_RPC_HOST', '127.0.0.1')),
            ('rpcuser', os.environ['BITCOIND_RPC_USER']),
            ('rpcpassword', os.environ['BITCOIND_RPC_PASSWORD']),
        ]
        for line in lines:
            conf_file.write('='.join(line) + '\n')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=5003)
