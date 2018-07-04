from collections import namedtuple
import os

from flask_admin.model import BaseModelView
from wtforms import Form

from app.lnd_client.grpc_generated.rpc_pb2 import Peer, Channel
from app.lnd_client.lightning_client import LightningClient

LND_Model = namedtuple('LND_Model', ['get_query', 'primary_key'])

class LNDModelView(BaseModelView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rpc_uri = os.environ.get('LND_RPC_URI', '127.0.0.1:10009')
        peer_uri = os.environ.get('LND_PEER_URI', '127.0.0.1:9735')
        self.ln = LightningClient(rpc_uri=rpc_uri, peer_uri=peer_uri)

    map = {
        Peer: LND_Model(get_query='get_peers', primary_key='pub_key'),
        Channel: LND_Model(get_query='get_channels', primary_key='chan_id')
    }

    can_view_details = True
    details_modal = True
    can_delete = False
    can_edit = False

    def get_one(self, record_id):
        record_count, records = self.get_list()
        return [r for r in records
                if str(getattr(r, self.map[self.model].primary_key)) == str(record_id)][0]

    def get_pk_value(self, model):
        return getattr(model, self.map[self.model].primary_key)

    def get_list(self, page=None, sort_field=None, sort_desc=None, search=None,
                       filters=None, page_size=None):

        results = getattr(self.ln, self.map[self.model].get_query)()

        if sort_field is not None:
            results.sort(key=lambda x: getattr(x, sort_field),
                         reverse=sort_desc)

        return len(results), results

    def create_model(self, form):
        pass

    def update_model(self, form, model):
        pass

    def delete_model(self, model):
        return NotImplementedError()

    def scaffold_form(self):
        class MyForm(Form):
            pass

        return MyForm

    def scaffold_list_form(self, widget=None, validators=None):
        pass

    def scaffold_list_columns(self):
        columns = [field.name for field in self.model.DESCRIPTOR.fields]
        return columns

    def scaffold_sortable_columns(self):
        columns = [field.name for field in self.model.DESCRIPTOR.fields]
        return columns
