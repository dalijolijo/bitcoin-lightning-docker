import os
from flask_admin.model import BaseModelView
from wtforms import Form

from app.lnd_client.grpc_generated.rpc_pb2 import Peer, Channel
from app.lnd_client.lightning_client import LightningClient


class LNDModelView(BaseModelView):
    def get_pk_value(self, model):
        key_map = {
            Peer: 'pub_key',
            Channel: 'chan_id'
        }
        return getattr(self.model, key_map[self.model])

    def scaffold_list_columns(self):
        columns = [field.name for field in self.model.DESCRIPTOR.fields]
        return columns

    def get_list(self, page, sort_field, sort_desc, search, filters,
                 page_size=None):
        rpc_uri = os.environ.get('LND_RPC_URI', '127.0.0.1:10009')
        peer_uri = os.environ.get('LND_PEER_URI', '127.0.0.1:9735')
        ln = LightningClient(rpc_uri=rpc_uri, peer_uri=peer_uri)
        query_map = {
            Peer: (ln.get_peers, 'peers'),
            Channel: (ln.get_channels, 'channels')
        }
        results = getattr(query_map[self.model][0](), query_map[self.model][1])
        return len(results), results


    def scaffold_sortable_columns(self):
        return []

    def scaffold_form(self):
        class MyForm(Form):
            pass

        # Do something
        return MyForm