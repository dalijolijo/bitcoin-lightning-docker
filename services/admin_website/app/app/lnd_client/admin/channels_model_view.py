from flask import flash
from flask_admin.babel import gettext
from flask_admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE
from flask_admin.model.fields import AjaxSelectField
from grpc import StatusCode

from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import (
    Channel,
    OpenChannelRequest,
    Peer
)


class PeersAjaxModelLoader(AjaxModelLoader):
    def __init__(self, name, model, **options):
        super(PeersAjaxModelLoader, self).__init__(name, options)

        self.model = model

    def format(self, model):
        if model is None:
            return '', ''
        return model.pub_key, model.pub_key + '@' + model.address

    def get_one(self, pk):
        return [r for r in LNDModelView(Channel).ln.get_peers()
                if r.pub_key == pk][0]

    def get_list(self, query, offset=0, limit=DEFAULT_PAGE_SIZE):
        pub_keys = LNDModelView(Channel).ln.get_peers()
        return pub_keys


class ChannelsModelView(LNDModelView):
    peer_ajax_loader = PeersAjaxModelLoader('node_pubkey_string', options=None,
                                            model=Peer,
                                            placeholder='Select node pubkey')

    can_create = True
    create_form_class = OpenChannelRequest
    get_query = 'get_channels'
    primary_key = 'chan_id'

    column_default_sort = 'chan_id'
    form_excluded_columns = ['node_pubkey']
    form_ajax_refs = {
        'node_pubkey_string': peer_ajax_loader
    }



    def scaffold_form(self):
        form_class = super(ChannelsModelView, self).scaffold_form()
        old = form_class.node_pubkey_string
        ajax_field = AjaxSelectField(loader=self.peer_ajax_loader,
                                     label='node_pubkey_string',
                                     allow_blank=True,
                                     description=old.kwargs['description'])
        form_class.local_funding_amount.kwargs['default'] = 60000
        form_class.push_sat.kwargs['default'] = 0
        form_class.target_conf.kwargs['default'] = 3
        form_class.sat_per_byte.kwargs['default'] = 250
        form_class.min_htlc_msat.kwargs['default'] = 1
        form_class.node_pubkey_string = ajax_field
        return form_class

    def create_model(self, form):
        data = form.data
        data['node_pubkey_string'] = data['node_pubkey_string'].pub_key
        try:
            response = self.ln.open_channel(**data)
        except Exception as exc:
            if hasattr(exc, '_state'):
                flash(gettext(exc._state.details), 'error')
            else:
                flash(gettext(str(exc)))
            return False

        if response.code() == StatusCode.UNKNOWN:
            flash(gettext(response._state.details), 'error')
            return False
        else:
            new_channel = [c for c in self.ln.get_channels()
                           if c.remote_pubkey == data['node_pubkey_string']][0]
            return new_channel
