from django.conf.global_settings import DATE_INPUT_FORMATS
from django.db.models import DateField
from django.forms import *
from django.forms.widgets import DateTimeBaseInput

from app_empresa.app_reg_empresa.models import Empresa


class EmpresaForm(ModelForm):
    class Meta:
        model = Empresa
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
            'aperturada': DateInput(format='%Y-%m-%d',
                attrs={
                    'type': 'date',
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
            ),
            'issuing_point_code': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un código de punto de emisión',
                    'autocomplete': 'off'
                }
            ),
            'business_name': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un nombre de razón social',
                    'autocomplete': 'off'
                }
            ),
            'main_address': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una dirección principal',
                    'autocomplete': 'off'
                }
            ),
            'tradename': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un nombre comercial'}),
            'establishment_address': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese una dirección establecimiento'}),
            'establishment_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un código de establecimiento'}),
            'special_taxpayer': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un número de resolución'}),
            'obligated_accounting': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'environment_type': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'emission_type': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'retention_agent': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'mobile': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un teléfono celular'}),
            'phone': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un teléfono convencional'}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un email'}),
            'website': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese una dirección web'}),
            'description': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese una descripción'}),
            'iva': TextInput(attrs={'class': 'form-control',}),
            'vat_percentage': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'electronic_signature_key': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la clave de la firma electrónica'}),
            'email_host': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el servidor de correo'}),
            'email_port': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el puerto de servidor de correo'}),
            'email_host_user': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el username del servidor de correo'}),
            'email_host_password': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el password del servidor de correo'}),

        }
