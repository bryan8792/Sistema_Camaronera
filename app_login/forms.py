from django.contrib.auth.forms import AuthenticationForm
from django.forms import *

class AuthenticationForm(ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'username': TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Ingrese un usuario',
                    'autocomplete':'off'
                }
            ),
            'password': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese un password',
                    'autocomplete': 'off'
                }
            )

        }

