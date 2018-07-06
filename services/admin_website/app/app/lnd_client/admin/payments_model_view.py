from flask import flash
from flask_admin.babel import gettext

from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import SendRequest


class PaymentsModelView(LNDModelView):
    can_create = True
    create_form_class = SendRequest
    get_query = 'get_payments'
    primary_key = 'payment_hash'

    def scaffold_form(self):
        form_class = super(PaymentsModelView, self).scaffold_form()
        return form_class

    def create_model(self, form):
        try:
            data = form.data
            data = {k: v for k, v in data.items() if data[k]}
            response = self.ln.send_payment_sync(**data)
            if hasattr(response, 'payment_error'):
                flash(gettext(str(response.payment_error)))
            print(response)
        except Exception as exc:
            if hasattr(exc, '_state'):
                flash(gettext(exc._state.details), 'error')
            else:
                flash(gettext(str(exc)))
        return
