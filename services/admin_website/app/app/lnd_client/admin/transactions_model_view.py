from flask import flash
from flask_admin.babel import gettext

from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import SendCoinsRequest


class TransactionsModelView(LNDModelView):
    can_create = True
    create_form_class = SendCoinsRequest
    get_query = 'get_transactions'
    primary_key = 'tx_hash'

    def scaffold_form(self):
        form_class = super(TransactionsModelView, self).scaffold_form()
        return form_class
