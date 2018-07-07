import codecs

from flask import flash
from flask_admin.babel import gettext
from google.protobuf.json_format import MessageToDict

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
        data = form.data
        data = {k: v for k, v in data.items() if data[k]}
        try:
            response = self.ln.send_payment_sync(**data)
        except Exception as exc:
            if hasattr(exc, '_state'):
                flash(gettext(exc._state.details), 'error')
            else:
                flash(gettext(str(exc)))
            return False

        if response.payment_error:
            flash(gettext(str(response.payment_error)))
            return False
        else:
            decoded_pay_req = self.ln.decode_payment_request(pay_req=data['payment_request'])
            payments = self.ln.get_payments()
            new_payment = [p for p in payments
                           if p.payment_hash == decoded_pay_req.payment_hash ]
            return new_payment[0]
