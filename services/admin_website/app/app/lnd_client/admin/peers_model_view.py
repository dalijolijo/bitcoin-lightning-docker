from flask import flash
from flask_admin.babel import gettext

from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import LightningAddress


class PeersModelView(LNDModelView):
    can_create = True
    create_form_class = LightningAddress

    def create_model(self, form):
        try:
            self.ln.connect(**form.data)
        except Exception as exc:
            flash(gettext(exc._state.details), 'error')
        return
