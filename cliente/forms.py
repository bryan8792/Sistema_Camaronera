from django import forms
from .models import *

class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': 'Ingrese un número de cedula o ruc',
            }),
            'movil': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': 'Ingrese un número de teléfono',
            }),
            'nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'birthdate',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#birthdate'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': 'Ingrese una dirección'
            }),
            'identification_type': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
        }
        exclude = ['usuario']


class ClientUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in self.visible_fields():
            if type(i.field) in [forms.CharField, forms.ImageField, forms.FileField, forms.EmailField]:
                i.field.widget.attrs.update({
                    'class': 'form-control',
                    'autocomplete': 'off'
                })
        self.fields['first_name'].widget.attrs['autofocus'] = True

    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'image'
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Ingrese sus nombres'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Ingrese su correo electrónico'}),
        }
        exclude = ['username', 'groups', 'is_active', 'is_change_password', 'is_staff', 'user_permissions', 'date_joined', 'last_login', 'is_superuser', 'email_reset_token']
