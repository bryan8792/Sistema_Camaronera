
from django.forms import *
from app_inventario.app_categoria.models import Categoria

class CategoriaForm(ModelForm):
    class Meta:
        model = Categoria
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un nombre',
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

        # exclude = ['user_creador', 'user_actualizo']