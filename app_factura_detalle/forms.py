from django.conf.global_settings import DATE_INPUT_FORMATS
from django.db.models import DateField
from django.forms import *
from django.forms.widgets import DateTimeBaseInput

from app_factura_detalle.models import Factura


class FacturaForm(ModelForm):
    class Meta:
        model = Factura
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Ingrese un nombre',
                    'autocomplete':'off'
                }
            ),
            'ruc': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un RUC',
                    'autocomplete': 'off'
                }
            ),
            'direccion': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Dirección',
                    'autocomplete': 'off'
                }
            ),
            'siglas': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese las Siglas',
                    'autocomplete': 'off'
                }
            ),
            'aperturada': DateInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'actividad': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese la Actividad',
                    'autocomplete': 'off'
                }
            )

        }
