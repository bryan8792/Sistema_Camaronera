
from django.forms import *
from app_inventario.app_categoria.models import Producto

OPCIONES_PRESENTACION = (
    ('----------', '---------'),
    ('SACO', 'SACO'),
    ('GALON', 'GALON'),
    ('TACHO', 'TACHO'),
    ('FRASCO', 'FRASCO'),
    ('FUNDA', 'FUNDA'),
    ('CANECA', 'CANECA'),
)

OPCIONES_MEDIDA = (
    ('----------', '---------'),
    ('LB', 'LIBRAS'),
    ('KG', 'KILOGRAMOS'),
    ('LT', 'LITROS'),
)

OPCIONES_APLICACION = (
    ('----------', '---------'),
    ('SC', 'SACOS'),
    ('CA', 'CANECAS'),
    ('LT', 'LITROS'),
    ('LB', 'LIBRAS'),
    ('KG', 'KILOS'),
    ('GR', 'GRAMOS'),
    ('ML', 'MILILITROS'),
    ('FD', 'FUNDA'),
)

OPCIONES_SUBCATEGORIA = (
    ('----------', '---------'),
    ('BALANCEADO', 'BALANCEADO'),
    ('CAL', 'CAL'),
    ('CERO FISH', 'CERO FISH'),
    ('MELAZA', 'MELAZA'),
    ('FERTILIZANTE', 'FERTILIZANTE'),
    ('MEDICAMENTO CAMARON', 'MEDICAMENTO CAMARON'),
    ('TRATAMIENTO AGUA', 'TRATAMIENTO AGUA'),
    ('TRATAMIENTO SUELO', 'TRATAMIENTO SUELO'),
    ('VITAMINA CAMARON', 'VITAMINA CAMARON'),
)

class ProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un nombre',
                    'autocomplete': 'off'
                }
            ),
            'categoria': Select(
                attrs={
                    'class': 'form-control select2',
                    'autocomplete': 'off'
                }
            ),
            'gramaje': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el Gramaje',
                    'autocomplete': 'off'
                }
            ),
            'descripcion': Select(choices=OPCIONES_SUBCATEGORIA,
                attrs={
                    'class': 'form-control select2'
                }
            ),
            'presentacion': Select(choices=OPCIONES_PRESENTACION,
                attrs={
                    'class': 'form-control select2'
                }
            ),
            'peso_presentacion': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el Peso de la presentación',
                    'autocomplete': 'off'
                }
            ),
            'unid_medida': Select(choices=OPCIONES_MEDIDA,
                attrs={
                    'class': 'form-control select2'
                }
            ),
            'unid_aplicacion': Select(choices=OPCIONES_APLICACION,
                attrs={
                    'class': 'form-control select2'
                }
            ),
            'minimo_stock': NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Stock Minimo',
                    'autocomplete': 'off'
                }
            ),
            'costo': NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese su Costo',
                    'autocomplete': 'off'
                }
            ),
            'costo_aplicacion': NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese su Costo en aplicacion',
                    'autocomplete': 'off'
                }
            ),
            'stock': NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese su Stock',
                    'autocomplete': 'off'
                }
            ),

            }