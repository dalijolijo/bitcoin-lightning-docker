from flask import flash
from flask_admin.babel import gettext
from flask_admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE
from flask_admin.model.fields import AjaxSelectField
from wtforms import SelectField

from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import OpenChannelRequest, Channel, \
    Peer


class PeersAjaxModelLoader(AjaxModelLoader):
    def __init__(self, name, model, **options):
        super(PeersAjaxModelLoader, self).__init__(name, options)

        self.model = model

    def format(self, model):
        if model is None:
            return '', ''
        return model.pub_key, model.pub_key

    def get_one(self, pk):
        pass

    def get_list(self, query, offset=0, limit=DEFAULT_PAGE_SIZE):
        pub_keys = LNDModelView(Channel).ln.get_peers()
        return pub_keys


class ChannelsModelView(LNDModelView):
    peer_ajax_loader = PeersAjaxModelLoader('node_pubkey_string', options=None, model=Peer,
                                            placeholder='Select node pubkey')

    can_create = True
    create_form_class = OpenChannelRequest
    form_excluded_columns = ['node_pubkey']
    form_ajax_refs = {
        'node_pubkey_string': peer_ajax_loader
    }

    def scaffold_form(self):
        form_class = super(ChannelsModelView, self).scaffold_form()
        old = form_class.node_pubkey_string
        form_class.node_pubkey_string = AjaxSelectField(loader=self.peer_ajax_loader,
                                                        label='node_pubkey_string',
                                                        allow_blank=True,
                                                        description=old.kwargs['description'])
        return form_class

    def create_model(self, form):
        try:
            self.ln.open_channel(**form.data)
        except Exception as exc:
            flash(gettext(exc._state.details), 'error')
        return