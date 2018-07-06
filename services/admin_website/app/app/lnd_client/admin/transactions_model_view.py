from flask_admin import expose
from google.protobuf.json_format import MessageToDict

from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import SendCoinsRequest


class TransactionsModelView(LNDModelView):
    can_create = True
    create_form_class = SendCoinsRequest
    get_query = 'get_transactions'
    primary_key = 'tx_hash'

    list_template = 'admin/transactions_list.html'

    def scaffold_form(self):
        form_class = super(TransactionsModelView, self).scaffold_form()
        return form_class

    @expose('/')
    def index_view(self):
        balance = self.ln.get_wallet_balance()
        self._template_args['balance'] = MessageToDict(balance)
        return super(TransactionsModelView, self).index_view()
