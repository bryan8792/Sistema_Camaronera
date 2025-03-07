
from django.forms import *

OPCIONES_EMPRESAS = (
    ('----------', '---------'),
    ('PSM', 'PESQUERA SAN MIGUEL'),
    ('BIO', 'BIOCASCAJAL'),
)

class ReportForm(Form):
    date_range = CharField(widget=TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'id': 'date_range'
    }))

    date_range2 = CharField(widget=TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'id': 'date_range2'
    }))

    opcion_empresa = Select(choices=OPCIONES_EMPRESAS, attrs={
        'class': 'form-control select2'
    })
