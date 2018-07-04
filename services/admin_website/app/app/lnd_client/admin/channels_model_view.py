from wtforms import StringField, SelectField

from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import OpenChannelRequest, Channel


class ChannelsModelView(LNDModelView):
    can_create = True
    create_form_class = OpenChannelRequest
    form_excluded_columns = ['node_pubkey']

    def scaffold_form(self):
        form_class = super(ChannelsModelView, self).scaffold_form()
        old = form_class.node_pubkey_string
        pub_keys = [(p.pub_key, p.pub_key) for p in
                    LNDModelView(Channel).ln.get_peers()]
        pub_keys.insert(0, ('', ''))
        form_class.node_pubkey_string = SelectField('node_pubkey_string',
                                                    choices=pub_keys,
                                                    description=old.kwargs['description'])
        return form_class

    def create_model(self, form):
        print(form)
        pass
