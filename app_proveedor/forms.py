from django.forms import *

from app_proveedor.models import Proveedor

OPCIONES_GRUPO = (
    ('----------', '---------'),
    ('Proveedor', 'Proveedor'),
    ('Empleados', 'Empleados'),
    ('Socios', 'Socios'),
    ('Vendedor', 'Vendedor'),
)

OPCIONES_ESTADO = (
    ('----------', '---------'),
    ('Activo', 'Activo'),
    ('Inactivo', 'Inactivo'),
)


class ProveedorForm(ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'
        widgets = {
            'ruc': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un RUC',
                    'autocomplete': 'off'
                }
            ),
            'razon_soc': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Razon Social',
                    'autocomplete': 'off'
                }
            ),
            'nombre_com': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Nombre Comercial',
                    'autocomplete': 'off'
                }
            ),
            'actividad_com': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Actividad Comercial',
                    'autocomplete': 'off'
                }
            ),
            # 'cod_contable': TextInput(
            #     attrs={
            #         'class': 'form-control',
            #         'placeholder': 'Ingrese un Cod. Contable',
            #         'autocomplete': 'off'
            #     }
            # ),
            'cod_contable': Select(
                attrs={
                    'class': 'custom-select select2',
                    # 'multiple': 'multiple'
                }
            ),
            'grupo': Select(choices=OPCIONES_GRUPO,
                attrs={
                    'class': 'form-control select2'
                }
            ),
            'mail': Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese Correos',
                    'autocomplete': 'off'
                }
            ),
            'direccion1': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Dirección 1',
                    'autocomplete': 'off'
                }
            ),
            'direccion2': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Dirección 2',
                    'autocomplete': 'off'
                }
            ),
            'direccion3': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Dirección 3',
                    'autocomplete': 'off'
                }
            ),
            'ciudad': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese la Ciudad',
                    'autocomplete': 'off'
                }
            ),
            'telef1': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese Telefono 1',
                    'autocomplete': 'off'
                }
            ),
            'telef2': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese Telefono 2',
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
            'estado': Select(choices=OPCIONES_ESTADO,
                attrs={
                    'class': 'form-control select2'
                }
            ),

        }
