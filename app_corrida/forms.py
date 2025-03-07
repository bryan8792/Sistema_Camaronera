
from django.forms import *
from app_corrida.models import PrecSiembraCuerp, PrecSiembraEnc


class PrecSiembraEncForm(ModelForm):
    class Meta:
        model = PrecSiembraEnc
        fields = '__all__'
        widgets = {
            'fecha': DateInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Año',
                    'autocomplete': 'off'
                }
            )
        }


class PrecSiembraCuerpForm(ModelForm):
    class Meta:
        model = PrecSiembraCuerp
        fields = '__all__'
        widgets = {
            'fecha_registro': DateInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Fecha de Registro',
                    'autocomplete': 'off',
                    'type': 'date'
                }
            ),
            'fecha_compra': DateInput(
                attrs={
                    'class': 'form-control',
                    'name': 'fecha_compra',
                    'placeholder': 'Ingrese una Fecha de Compra',
                    'autocomplete': 'off',
                    'type': 'date'
                }
            ),
            'fecha_transferencia': DateInput(
                attrs={
                    'class': 'form-control',
                    'name': 'fecha_transferencia',
                    'placeholder': 'Ingrese una Fecha de Transferencia',
                    'autocomplete': 'off',
                    'type': 'date'
                }
            ),
            'comp_1': TextInput(
                attrs={
                    'class': 'form-control text-center monto',
                    'placeholder': 'Ingrese compa n.1',
                    'autocomplete': 'off'
                }
            ),
            'comp_2': TextInput(
                attrs={
                    'class': 'form-control text-center monto',
                    'placeholder': 'Ingrese compa n.2',
                    'autocomplete': 'off'
                }
            ),
            'comp_3': TextInput(
                attrs={
                    'class': 'form-control text-center monto',
                    'placeholder': 'Ingrese compa n.3',
                    'autocomplete': 'off'
                }
            ),
            'tot_comp': TextInput(
                attrs={
                    'class': 'form-control text-center',
                    'placeholder': 'Ingrese compa n.1',
                    'readonly': 'readonly',
                    'autocomplete': 'off',
                    'id': 'tot_comp_sum'
                }
            ),
            'producto': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese compa n.1',
                    'autocomplete': 'off'
                }
            ),
            'prod_cantidad': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese compa n.1',
                    'autocomplete': 'off'
                }
            ),
            'observacion': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese Una Observación',
                    'autocomplete': 'off',
                }
            ),

        }


class ReportForm(Form):
    date_range3 = CharField(widget=TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'id': 'date_range'
    }))