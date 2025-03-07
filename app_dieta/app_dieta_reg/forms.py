
from django.forms import *
from app_dieta.app_dieta_reg.models import AnioDieta, MesDieta, DiaDietaRegistro, DescripcionDieta, DetalleDiaDieta
from app_inventario.app_categoria.models import Producto


class AnioDietaForm(ModelForm):
    class Meta:
        model = AnioDieta
        fields = '__all__'
        widgets = {
            'anio_dieta': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Año',
                    'autocomplete': 'off'
                }
            )
        }


class MesDietaForm(ModelForm):
    class Meta:
        model = MesDieta
        fields = '__all__'
        widgets = {
            'mes_dieta': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Mes',
                    'autocomplete': 'off'
                }
            ),
            'fecha_dieta': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un RUC',
                    'autocomplete': 'off'
                }
            ),
            'descripcion': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Descripciónx',
                    'autocomplete': 'off'
                }
            )

        }


class RegistroDiaDietaForm(ModelForm):
    class Meta:
        model = DiaDietaRegistro
        fields = '__all__'
        widgets = {
            'mes_dieta': Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Mes',
                    'autocomplete': 'off'
                }
            ),
            'fecha': DateInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            )
        }


class DiaDietaForm(ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super(DiaDietaForm, self).__init__(*args, **kwargs)
    #     self.fields['insumo1'].queryset = Producto.objects.all()
    class Meta:
        model = DetalleDiaDieta
        fields = '__all__'
        widgets = {
            'fecha': DateInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Fecha',
                    'autocomplete': 'off'
                }
            ),
            'piscinas': Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un RUC',
                    'autocomplete': 'off'
                }
            ),
            'balanceado': Select(
                attrs={
                    'class': 'form-control select2'
                }
            ),
            'insumo1': Select(
                attrs={
                    'class': 'form-control select2'
                }
            ),
            'insumo2': Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Descripción',
                    'autocomplete': 'off'
                }
            ),
            'insumo3': Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Descripción',
                    'autocomplete': 'off'
                }
            ),
            'insumo4': Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Descripción',
                    'autocomplete': 'off'
                }
            )

        }


class DescripcionDietaForm(ModelForm):
    class Meta:
        model = DescripcionDieta
        fields = '__all__'
        widgets = {
            'fecha': DateInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un Año',
                    'autocomplete': 'off'
                }
            ),
            'descripcion': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una Descripción',
                    'autocomplete': 'off'
                }
            )
        }
