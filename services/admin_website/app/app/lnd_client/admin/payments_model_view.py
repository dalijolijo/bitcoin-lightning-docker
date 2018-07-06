from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import Payment


class PaymentsModelView(LNDModelView):
    can_create = False
    create_form_class = Payment

    def scaffold_form(self):
        form_class = super(PaymentsModelView, self).scaffold_form()
        return form_class
