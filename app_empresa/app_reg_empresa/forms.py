from django.conf.global_settings import DATE_INPUT_FORMATS
from django.db.models import DateField
from django.forms import *
from django.forms.widgets import DateTimeBaseInput
from app_empresa.app_reg_empresa.models import Empresa
from django.conf.global_settings import DATE_INPUT_FORMATS
from django.db.models import DateField
from django.forms import *
from django.forms.widgets import DateTimeBaseInput
import re

from app_empresa.app_reg_empresa.models import Empresa


class EmpresaForm(ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'
        exclude = ['scheme']
        widgets = {
            'schema_name': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: miempresa (solo minusculas y numeros)',
                    'autocomplete': 'off',
                    'pattern': '[a-z0-9]+',
                    'title': 'Solo letras minusculas y numeros, sin espacios ni caracteres especiales'
                }
            ),
            'nombre': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un nombre',
                    'autocomplete': 'off'
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
                    'placeholder': 'Ingrese una Direccion',
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
                    'placeholder': 'Ingrese un codigo de punto de emision',
                    'autocomplete': 'off'
                }
            ),
            'business_name': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un nombre de razon social',
                    'autocomplete': 'off'
                }
            ),
            'main_address': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una direccion principal',
                    'autocomplete': 'off'
                }
            ),
            'tradename': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un nombre comercial'}),
            'establishment_address': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese una direccion establecimiento'}),
            'establishment_code': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese un codigo de establecimiento'}),
            'special_taxpayer': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese un numero de resolucion'}),
            'obligated_accounting': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'environment_type': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'emission_type': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'retention_agent': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'mobile': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un telefono celular'}),
            'phone': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un telefono convencional'}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un email'}),
            'website': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese una direccion web'}),
            'description': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese una descripcion'}),
            'iva': TextInput(attrs={'class': 'form-control', }),
            'vat_percentage': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'electronic_signature_key': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese la clave de la firma electronica'}),
            'email_host': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el servidor de correo'}),
            'email_port': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese el puerto de servidor de correo'}),
            'email_host_user': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese el username del servidor de correo'}),
            'email_host_password': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese el password del servidor de correo'}),
        }

    def clean_schema_name(self):
        """Validar el nombre del esquema para multi-tenant"""
        schema_name = self.cleaned_data.get('schema_name')

        if schema_name:
            schema_name = schema_name.lower().strip()

            if not re.match('^[a-z0-9]+$', schema_name):
                raise ValidationError(
                    'Solo se permiten letras minusculas y numeros, sin espacios ni caracteres especiales')

            if len(schema_name) < 3:
                raise ValidationError('El nombre del esquema debe tener al menos 3 caracteres')

            reserved = ['public', 'admin', 'www', 'api', 'static', 'media', 'localhost', 'mail', 'ftp', 'ssh']
            if schema_name in reserved:
                raise ValidationError(f'El nombre "{schema_name}" esta reservado y no se puede usar')

            if not self.instance.pk:
                from app_tenant.models import Scheme
                if Scheme.objects.filter(schema_name=schema_name).exists():
                    raise ValidationError(f'Ya existe una empresa con el esquema "{schema_name}"')

        return schema_name


class FiltroFechaForm(Form):
    fecha_inicio = DateField(
        label='Fecha Inicio',
        widget=DateInput(attrs={'type': 'date'})
    )
    fecha_fin = DateField(
        label='Fecha Fin',
        widget=DateInput(attrs={'type': 'date'})
    )
    empresa = ModelChoiceField(
        queryset=Empresa.objects.filter(estado=True),
        required=False,
        empty_label="Todas las empresas"
    )

# class PiscinaForm(ModelForm):
#     class Meta:
#         model = Piscinas
#         fields = ['numero', 'empresa', 'area_hectareas', 'ubicacion',
#                   'fecha_construccion', 'profundidad_promedio', 'capacidad_m3', 'activo']
#         widgets = {
#             'fecha_construccion': DateInput(attrs={'type': 'date'}),
#             'area_hectareas': NumberInput(attrs={'step': '0.01'}),
#             'profundidad_promedio': NumberInput(attrs={'step': '0.01'}),
#             'capacidad_m3': NumberInput(attrs={'step': '0.01'}),
#         }
