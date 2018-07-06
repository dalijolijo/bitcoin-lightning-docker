from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import Invoice


class InvoicesModelView(LNDModelView):
    can_create = False
    create_form_class = Invoice

    def scaffold_form(self):
        form_class = super(InvoicesModelView, self).scaffold_form()
        return form_class
