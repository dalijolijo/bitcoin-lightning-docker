import codecs

from flask import flash
from flask_admin import expose
from flask_admin.babel import gettext
from flask_admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE
from flask_admin.model.fields import AjaxSelectField
from google.protobuf.json_format import MessageToDict
from grpc import StatusCode
from markupsafe import Markup

from app.formatters.lnd import pub_key_formatter
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
        formatted = pub_key_formatter(view=None, context=None, model=model, name='pub_key')
        return model.pub_key, Markup(formatted).striptags()

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
    list_template = 'admin/channels_list.html'

    column_formatters = {
        'remote_pubkey': pub_key_formatter
    }

    def scaffold_form(self):
        form_class = super(ChannelsModelView, self).scaffold_form()
        old = form_class.node_pubkey_string
        ajax_field = AjaxSelectField(loader=self.peer_ajax_loader,
                                     label='node_pubkey_string',
                                     allow_blank=True,
                                     description=old.kwargs['description'])
        form_class.local_funding_amount.kwargs['default'] = 500000
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
            response = self.ln.open_channel_sync(**data)
        except Exception as exc:
            if hasattr(exc, '_state'):
                flash(gettext(exc._state.details), 'error')
            else:
                flash(gettext(str(exc)))
            return False

        if hasattr(response, 'code') and response.code() == StatusCode.UNKNOWN:
            flash(gettext(response._state.details), 'error')
            return False
        else:
            txid = codecs.decode(response.funding_txid_bytes , 'hex')
            outpoint = ':'.join([txid, str(response.output_index)])
            new_channel = [c for c in self.ln.get_channels()
                           if c.channel_point == outpoint][0]
            return new_channel

    @expose('/')
    def index_view(self):
        balance = self.ln.get_channel_balance()
        self._template_args['balance'] = MessageToDict(balance)
        return super(ChannelsModelView, self).index_view()
