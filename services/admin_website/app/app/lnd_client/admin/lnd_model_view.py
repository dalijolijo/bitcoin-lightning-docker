import json
import os

from flask_admin import expose
from flask_admin.model import BaseModelView
from wtforms import Form, StringField, IntegerField, BooleanField, validators

from app.lnd_client.lightning_client import LightningClient

wtforms_type_map = {
    3: IntegerField,  # int64
    4: IntegerField,  # uint64
    5: IntegerField,  # int32
    8: BooleanField,  # bool
    9: StringField,   # string
    12: StringField,  # bytes
    13: IntegerField, # uint32
}

class LNDModelView(BaseModelView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rpc_uri = os.environ.get('LND_RPC_URI', '127.0.0.1:10009')
        peer_uri = os.environ.get('LND_PEER_URI', '127.0.0.1:9735')
        self.ln = LightningClient(rpc_uri=rpc_uri, peer_uri=peer_uri)

    with open('rpc.swagger.json', 'r') as swagger_file:
        swagger = json.load(swagger_file)

    create_form_class = None
    get_query = None
    primary_key = None

    can_view_details = True
    details_modal = True
    create_modal = True
    can_delete = False
    can_edit = False

    list_template = 'admin/lnd_list.html'

    def get_one(self, record_id):
        record_count, records = self.get_list()
        return [r for r in records
                if str(getattr(r, self.primary_key)) == str(record_id)][0]

    def get_pk_value(self, model):
        return getattr(model, self.primary_key)

    def get_list(self, page=None, sort_field=None, sort_desc=None, search=None,
                       filters=None, page_size=None):

        results = getattr(self.ln, self.get_query)()

        if sort_field is not None:
            results.sort(key=lambda x: getattr(x, sort_field),
                         reverse=sort_desc)

        return len(results), results

    def create_model(self, form):
        return NotImplementedError()

    def update_model(self, form, model):
        return NotImplementedError()

    def delete_model(self, model):
        return NotImplementedError()

    def scaffold_form(self):
        class NewForm(Form):
            pass
        if self.create_form_class is None:
            return NewForm

        for field in self.create_form_class.DESCRIPTOR.fields:

            if self.form_excluded_columns and field.name in self.form_excluded_columns:
                continue

            field_type = field.type

            if field_type == 11: # Todo: handle "message" type, which is a nested object
                continue

            FormClass = wtforms_type_map[field_type]
            description = self.swagger['definitions']['lnrpc' + self.create_form_class.__name__]['properties'][field.name]
            description = description.get('title') or description.get('description')
            if description:
                description = description.replace('/ ', '')
            form_field = FormClass(field.name,
                                   default=field.default_value or None,
                                   description=description,
                                   validators=[validators.optional()]
                                   )
            setattr(NewForm, field.name, form_field)
        return NewForm

    def scaffold_list_form(self, widget=None, validators=None):
        pass

    def scaffold_list_columns(self):
        columns = [field.name for field in self.model.DESCRIPTOR.fields]
        return columns

    def scaffold_sortable_columns(self):
        columns = [field.name for field in self.model.DESCRIPTOR.fields]
        return columns