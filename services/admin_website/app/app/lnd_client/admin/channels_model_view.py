from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import OpenChannelRequest


class ChannelsModelView(LNDModelView):
    can_create = True
    create_form_class = OpenChannelRequest
    form_excluded_columns = ['node_pubkey']

    def create_model(self, form):
        print(form)
        pass

