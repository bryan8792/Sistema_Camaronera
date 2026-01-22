
from tkinter.tix import Select
from django.forms import *

from app_contabilidad_planCuentas.models import PlanCuenta
from app_empresa.app_reg_empresa.models import Empresa
from app_inventario.app_categoria.models import Producto
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
    ('PISCINA PC-1', 'PISCINA PC-1'),
    ('PISCINA PC-25', 'PISCINA PC-25'),
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
                    'type': 'date',
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
            'cod_contable': NumberInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),

        }


class StockAccountingForm(ModelForm):
    """
    Form for updating stock with accounting plan selection
    Actualiza registros existentes de Total_Stock con plan de cuentas
    """
    plan_cuenta = ModelChoiceField(
        queryset=PlanCuenta.objects.none(),
        required=True,  # Changed to required=True to force account assignment
        empty_label="--- Seleccione una Cuenta Contable ---",
        help_text="Seleccione el plan de cuentas para este producto",
        widget=Select(attrs={
            'class': 'form-control select2',
            'id': 'id_plan_cuenta',
            'data-placeholder': 'Buscar cuenta contable...'
        })
    )

    nombre_empresa = ModelChoiceField(
        queryset=Empresa.objects.all(),
        empty_label="--- Seleccione Empresa ---",
        widget=Select(attrs={
            'class': 'form-control',
            'id': 'id_nombre_empresa'
        })
    )

    nombre_prod = ModelChoiceField(
        queryset=Producto.objects.none(),  # Start empty, will be populated via AJAX
        empty_label="--- Seleccione Producto ---",
        widget=Select(attrs={
            'class': 'form-control select2',
            'id': 'id_nombre_prod'
        })
    )

    class Meta:
        model = Total_Stock
        fields = ['nombre_empresa', 'nombre_prod', 'plan_cuenta']

    def __init__(self, *args, **kwargs):
        empresa_obj = kwargs.pop('empresa_obj', None)
        producto_obj = kwargs.pop('producto_obj', None)
        readonly_mode = kwargs.pop('readonly_mode', False)

        super().__init__(*args, **kwargs)

        if readonly_mode:
            self.fields['nombre_empresa'].widget.attrs['disabled'] = 'disabled'
            self.fields['nombre_empresa'].widget.attrs['readonly'] = 'readonly'
            self.fields['nombre_prod'].widget.attrs['disabled'] = 'disabled'
            self.fields['nombre_prod'].widget.attrs['readonly'] = 'readonly'

        if empresa_obj:
            self.fields['plan_cuenta'].queryset = PlanCuenta.objects.filter(
                empresa=empresa_obj,
                estado=True
            ).order_by('codigo')

            if producto_obj:
                self.fields['nombre_prod'].queryset = Producto.objects.filter(
                    id=producto_obj.id
                )
            else:
                productos_con_stock = Total_Stock.objects.filter(
                    nombre_empresa=empresa_obj
                ).values_list('nombre_prod_id', flat=True).distinct()

                self.fields['nombre_prod'].queryset = Producto.objects.filter(
                    id__in=productos_con_stock,
                    estado=True
                ).order_by('nombre')

        if self.instance and self.instance.pk:
            if self.instance.nombre_empresa:
                self.fields['plan_cuenta'].queryset = PlanCuenta.objects.filter(
                    empresa=self.instance.nombre_empresa,
                    estado=True
                ).order_by('codigo')

    def clean(self):
        cleaned_data = super().clean()

        if self.fields['nombre_empresa'].widget.attrs.get('disabled'):
            if 'nombre_empresa' not in cleaned_data or not cleaned_data['nombre_empresa']:
                cleaned_data['nombre_empresa'] = self.initial.get('nombre_empresa')

        if self.fields['nombre_prod'].widget.attrs.get('disabled'):
            if 'nombre_prod' not in cleaned_data or not cleaned_data['nombre_prod']:
                cleaned_data['nombre_prod'] = self.initial.get('nombre_prod')

        return cleaned_data







