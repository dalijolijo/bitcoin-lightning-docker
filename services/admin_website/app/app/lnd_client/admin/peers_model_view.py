from flask import flash
from flask_admin.babel import gettext
from wtforms import StringField

from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import LightningAddress, Peer


class PeersModelView(LNDModelView):
    can_create = True
    can_delete = True
    create_form_class = LightningAddress
    get_query = 'get_peers'
    primary_key = 'pub_key'

    column_default_sort = 'pub_key'

    def scaffold_form(self):
        form_class = super(PeersModelView, self).scaffold_form()
        form_class.pubkey_at_host = StringField('pubkey@host')
        return form_class


    def create_model(self, form):
        if form.data.get('pubkey_at_host'):
            pubkey = form.data.get('pubkey_at_host').split('@')[0]
            host = form.data.get('pubkey_at_host').split('@')[1]
        else:
            pubkey = form.data.get('pubkey')
            host = form.data.get('host')
        try:
            self.ln.connect_peer(pubkey=pubkey, host=host)
        except Exception as exc:
            flash(gettext(exc._state.details), 'error')
            return
        new_peer = [p for p in self.ln.get_peers() if p.pub_key == pubkey]
        return new_peer

    def delete_model(self, model: Peer):
        try:
            response = self.ln.disconnect_peer(pub_key=model.pub_key)
            return True
        except Exception as exc:
            if hasattr(exc, '_state'):
                flash(gettext(exc._state.details), 'error')
            else:
                flash(gettext(str(exc)))
            return False