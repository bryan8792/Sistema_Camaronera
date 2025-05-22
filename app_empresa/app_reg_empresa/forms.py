from django.conf.global_settings import DATE_INPUT_FORMATS
from django.db.models import DateField
from django.forms import *
from django.forms.widgets import DateTimeBaseInput

from app_empresa.app_reg_empresa.models import Empresa, TipoCosto, CostoOperativo, Ciclo, Produccion, Piscinas


class EmpresaForm(ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'
        widgets = {
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
            'establishment_address': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese una dirección establecimiento'}),
            'establishment_code': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese un código de establecimiento'}),
            'special_taxpayer': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese un número de resolución'}),
            'obligated_accounting': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'environment_type': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'emission_type': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'retention_agent': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'mobile': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un teléfono celular'}),
            'phone': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un teléfono convencional'}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese un email'}),
            'website': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese una dirección web'}),
            'description': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese una descripción'}),
            'iva': TextInput(attrs={'class': 'form-control', }),
            'vat_percentage': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'electronic_signature_key': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese la clave de la firma electrónica'}),
            'email_host': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el servidor de correo'}),
            'email_port': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese el puerto de servidor de correo'}),
            'email_host_user': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese el username del servidor de correo'}),
            'email_host_password': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese el password del servidor de correo'}),

        }


class TipoCostoForm(ModelForm):
    class Meta:
        model = TipoCosto
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del tipo de costo'}),
            'descripcion': Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese una descripción', 'rows': 3}),
        }

class CostoOperativoForm(ModelForm):
    class Meta:
        model = CostoOperativo
        fields = ['piscina', 'tipo_costo', 'fecha', 'monto', 'descripcion', 'comprobante', 'proveedor']
        widgets = {
            'piscina': Select(attrs={'class': 'form-control select2'}),
            'tipo_costo': Select(attrs={'class': 'form-control select2'}),
            'fecha': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monto': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'descripcion': Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comprobante': TextInput(attrs={'class': 'form-control'}),
            'proveedor': Select(attrs={'class': 'form-control select2'}),
        }


class CicloForm(ModelForm):
    class Meta:
        model = Ciclo
        fields = ['piscina', 'nombre', 'fecha_inicio', 'fecha_fin', 'densidad_siembra', 'cantidad_larvas',
                  'activo']
        widgets = {
            'piscina': Select(attrs={'class': 'form-control select2'}),
            'nombre': TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': False}),
            'densidad_siembra': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'cantidad_larvas': NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'activo': CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProduccionForm(ModelForm):
    class Meta:
        model = Produccion
        fields = ['piscina', 'ciclo', 'fecha_cosecha', 'cantidad_kg', 'precio_venta_kg', 'talla_promedio',
                  'cliente', 'factura', 'observaciones']
        widgets = {
            'piscina': Select(attrs={'class': 'form-control select2'}),
            'ciclo': Select(attrs={'class': 'form-control select2'}),
            'fecha_cosecha': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cantidad_kg': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'precio_venta_kg': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'talla_promedio': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'cliente': TextInput(attrs={'class': 'form-control'}),
            'factura': TextInput(attrs={'class': 'form-control'}),
            'observaciones': Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar ciclos activos
        self.fields['ciclo'].queryset = Ciclo.objects.filter(activo=True)

        # Si ya hay una piscina seleccionada, filtrar ciclos por esa piscina
        if 'piscina' in self.data:
            try:
                piscina_id = int(self.data.get('piscina'))
                self.fields['ciclo'].queryset = Ciclo.objects.filter(piscina_id=piscina_id, activo=True)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.piscina:
            self.fields['ciclo'].queryset = Ciclo.objects.filter(piscina=self.instance.piscina, activo=True)

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
