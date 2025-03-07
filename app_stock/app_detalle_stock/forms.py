
from tkinter.tix import Select
from django.forms import *
from app_stock.app_detalle_stock.models import Producto_Stock, Total_Stock, InvoiceStock

OPCIONES_ESCOGER = (
    ('--------', '--------'),
    ('INGRESO', 'INGRESO'),
    ('EGRESO', 'EGRESO'),
)

PISCINAS_ESCOGER = (
    ('Todas las Piscinas', 'Todas las Piscinas'),
    ('PISCINA 1', 'PISCINA 1'),
    ('PISCINA 2', 'PISCINA 2'),
    ('PISCINA 3', 'PISCINA 3'),
    ('PISCINA 4', 'PISCINA 4'),
    ('PISCINA 5', 'PISCINA 5'),
    ('PISCINA 6', 'PISCINA 6'),
    ('PISCINA 7', 'PISCINA 7'),
    ('PISCINA 8', 'PISCINA 8'),
    ('PISCINA 9', 'PISCINA 9'),
    ('PISCINA 10', 'PISCINA 10'),
    ('PISCINA 11', 'PISCINA 11'),
    ('PISCINA 12', 'PISCINA 12'),
    ('PISCINA 13', 'PISCINA 13'),
    ('PISCINA 14', 'PISCINA 14'),
    ('PISCINA 15', 'PISCINA 15'),
    ('PISCINA 16', 'PISCINA 16'),
    ('PISCINA 17', 'PISCINA 17'),
    ('PISCINA 18', 'PISCINA 18'),
    ('PISCINA 19', 'PISCINA 19'),
    ('PISCINA 20', 'PISCINA 20'),
    ('PISCINA 21', 'PISCINA 21'),
    ('PISCINA 22', 'PISCINA 22'),
    ('PISCINA 23', 'PISCINA 23'),
    ('PISCINA 24', 'PISCINA 24'),
    ('PISCINA 25', 'PISCINA 25'),
    ('PISCINA 26', 'PISCINA 26'),
    ('PISCINA 27', 'PISCINA 27'),
    ('PISCINA 28', 'PISCINA 28'),
    ('PISCINA 29', 'PISCINA 29'),
    ('PISCINA 30', 'PISCINA 30'),
    ('PISCINA 31', 'PISCINA 31'),
    ('PISCINA 32', 'PISCINA 32'),
    ('PISCINA 33', 'PISCINA 33'),
    ('PISCINA 34', 'PISCINA 34'),
    ('PISCINA 35', 'PISCINA 35'),
    ('PISCINA 36', 'PISCINA 36'),
    ('PISCINA 37', 'PISCINA 37'),
    ('PISCINA 38', 'PISCINA 38'),
    ('PISCINA 39', 'PISCINA 39'),
    ('PISCINA 40', 'PISCINA 40'),
    ('PISCINA 41', 'PISCINA 41'),
    ('PISCINA 42', 'PISCINA 42'),
    ('PISCINA 43', 'PISCINA 43'),
    ('PISCINA 44', 'PISCINA 44'),
    ('PISCINA 45', 'PISCINA 45'),
)

class ProdStockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].widget.attrs['autoselect'] = False

    class Meta:
        model = Producto_Stock
        fields = '__all__'
        widgets = {
            'producto_empresa': Select(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'readonly': 'readonly'
                }
            ),
            'cantidad_usar': NumberInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'cantidad_ingreso': NumberInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'readonly': 'readonly'
                }
            ),
            'cantidad_egreso': NumberInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'readonly': 'readonly'
                }
            ),
            'tipo': Select(
                choices=OPCIONES_ESCOGER,
                attrs={
                    'class': 'form-control select2'
                }
            ),
            'piscinas': Select(
                choices=PISCINAS_ESCOGER,
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%',
                    # 'multiple': 'multiple'
                }
            ),
            'fecha_ingreso': DateInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'required': True
                },
                format='%Y-%m-%d'
            ),
            'numero_guia': TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'placeholder': 'Ingrese un número de guia',
                    'required': True
                }
            ),
            'responsable_ingreso': TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'placeholder': 'Ingrese un responsable',
                    'required': True
                }
            ),
            'proveedor': Select(
                attrs={
                    'class': 'form-control select2',
                    'autocomplete': 'off'
                }
            ),
            'observacion': Textarea(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'placeholder': 'Ingrese una Observación'
                }
            ),
            'iva': NumberInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'ivacalc': NumberInput(
                attrs={
                    'readonly': True,
                    'class': 'form-control',
                }
            ),
            'subtotal': NumberInput(
                attrs={
                    'readonly': True,
                    'class': 'form-control',
                }
            ),
            'total': NumberInput(
                attrs={
                    'readonly': True,
                    'class': 'form-control',
                }),
        }

      # exclude = ['piscinas']


class InvoiceStockForm(ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super(ProdStockForm, self).__init__(*args, **kwargs)
    #     self.fields['producto_empresa'].queryset = Total_Stock.objects.filter(nombre_empresa__siglas='PSM')

    class Meta:
        model = InvoiceStock
        fields = '__all__'
        widgets = {
            'fecha_ingreso': DateInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'required': True
                },
                format='%Y-%m-%d'
            ),
            'numero_guia': TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'placeholder': 'Ingrese un número de guia',
                    'required': True
                }
            ),
            'responsable_ingreso': TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'placeholder': 'Ingrese un responsable',
                    'required': True
                }
            ),
        }

        exclude = ['piscinas']


class ProdStockTotalForm(ModelForm):
    class Meta:
        model = Total_Stock
        fields = '__all__'
        widgets = {
            'nombre_prod': Select(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'nombre_empresa': Select(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'stock': NumberInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),


        }

