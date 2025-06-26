from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission
from app_user.models import User
from django.forms import ModelForm
from django.forms.widgets import (
    CheckboxInput, ClearableFileInput, Select, SelectMultiple,
    TextInput, EmailInput, PasswordInput, Textarea, NumberInput
)
from .models import Modulo, TipoModulo


class UserForm(ModelForm):
    # Campos adicionales
    image = forms.ImageField(required=False, label="Foto de Perfil")

    # Campos para permisos
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Grupos de Usuario",
        widget=SelectMultiple(attrs={'class': 'form-control select2', 'multiple': 'multiple'})
    )

    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        label="Permisos Específicos",
        widget=SelectMultiple(attrs={'class': 'form-control', 'multiple': 'multiple'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser']

        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa el nombre de usuario'
            }),
            'first_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa los nombres'
            }),
            'last_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa los apellidos'
            }),
            'email': EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa el correo electrónico'
            }),
            'is_superuser': CheckboxInput(attrs={
                'class': 'custom-control-input'
            }),
            'is_active': CheckboxInput(attrs={
                'class': 'custom-control-input'
            }),
            'is_staff': CheckboxInput(attrs={
                'class': 'custom-control-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widget para imagen
        self.fields['image'].widget = ClearableFileInput(attrs={
            'class': 'form-control-file'
        })


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nombres")
    last_name = forms.CharField(max_length=30, required=True, label="Apellidos")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    image = forms.ImageField(required=False, label="Foto de Perfil")

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Grupos de Usuario",
        widget=SelectMultiple(attrs={'class': 'form-control select2', 'multiple': 'multiple'})
    )

    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        label="Permisos Específicos",
        widget=SelectMultiple(attrs={'class': 'form-control', 'multiple': 'multiple'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',
                  'is_active', 'is_staff', 'is_superuser')

        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa el nombre de usuario'
            }),
            'first_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa los nombres'
            }),
            'last_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa los apellidos'
            }),
            'email': EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa el correo electrónico'
            }),
            'password1': PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa la contraseña'
            }),
            'password2': PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirma la contraseña'
            }),
            'is_superuser': CheckboxInput(attrs={
                'class': 'custom-control-input'
            }),
            'is_active': CheckboxInput(attrs={
                'class': 'custom-control-input'
            }),
            'is_staff': CheckboxInput(attrs={
                'class': 'custom-control-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widget para imagen
        self.fields['image'].widget = ClearableFileInput(attrs={
            'class': 'form-control-file'
        })

        # Asegurar que los permisos se carguen correctamente
        self.fields['user_permissions'].queryset = Permission.objects.all().select_related('content_type')


class GroupForm(forms.ModelForm):
    modulos = forms.ModelMultipleChoiceField(
        queryset=Modulo.objects.filter(activo=True),
        required=False,
        label="Módulos del Sistema",
        widget=SelectMultiple(attrs={'class': 'form-control select2', 'multiple': 'multiple'})
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
            'name': 'Nombre del Grupo',
            'permissions': 'Permisos del Sistema'
        }
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa el nombre del grupo'
            }),
            'permissions': SelectMultiple(attrs={
                'class': 'form-control select2',
                'multiple': 'multiple'
            })
        }


class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = ['nombre', 'url', 'icono', 'descripcion', 'tipo', 'orden', 'activo']
        labels = {
            'nombre': 'Nombre del Módulo',
            'url': 'URL del Módulo',
            'icono': 'Icono',
            'descripcion': 'Descripción',
            'tipo': 'Tipo de Módulo',
            'orden': 'Orden',
            'activo': 'Activo'
        }
        widgets = {
            'nombre': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del módulo'
            }),
            'url': TextInput(attrs={
                'class': 'form-control',
                'placeholder': '/ruta/del/modulo/'
            }),
            'icono': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fas fa-icon'
            }),
            'descripcion': Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del módulo'
            }),
            'tipo': Select(attrs={
                'class': 'form-control'
            }),
            'orden': NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'activo': CheckboxInput(attrs={
                'class': 'custom-control-input'
            })
        }


class TipoModuloForm(forms.ModelForm):
    class Meta:
        model = TipoModulo
        fields = ['nombre', 'descripcion', 'orden', 'activo']
        labels = {
            'nombre': 'Nombre del Tipo',
            'descripcion': 'Descripción',
            'orden': 'Orden',
            'activo': 'Activo'
        }
        widgets = {
            'nombre': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del tipo de módulo'
            }),
            'descripcion': Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del tipo de módulo'
            }),
            'orden': NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'activo': CheckboxInput(attrs={
                'class': 'custom-control-input'
            })
        }