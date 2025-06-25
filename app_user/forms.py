from django import forms
from django.contrib.auth.models import Group, Permission
from django.forms import *
from app_user.models import User, Modulo, TipoModulo, GrupoModulo


class UserForm(ModelForm):
    groups = ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=SelectMultiple(attrs={
            'class': 'form-control',
        }),
        label='Grupos'
    )
    user_permissions = ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=SelectMultiple(attrs={
            'class': 'form-control',
        }),
        label='Permisos'
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'username', 'password',
            'is_superuser', 'is_active', 'is_staff', 'imagen',
            'groups', 'user_permissions'
        )
        widgets = {
            'password': PasswordInput(render_value=True, attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese una Contraseña',
                'autocomplete': 'off'
            }),
            'username': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de usuario',
                'autocomplete': 'off'
            }),
            'first_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre',
                'autocomplete': 'off'
            }),
            'last_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el apellido',
                'autocomplete': 'off'
            }),
            'email': EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese un correo electrónico',
                'autocomplete': 'off'
            }),
            'is_superuser': CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'transform: scale(0.55); margin-top: 3px;'
            }),
            'is_active': CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'transform: scale(0.55); margin-top: 3px;'
            }),
            'is_staff': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'imagen': ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }


class GroupForm(ModelForm):
    modulos = ModelMultipleChoiceField(
        queryset=Modulo.objects.filter(activo=True),
        required=False,
        widget=CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
        }),
        label='Módulos'
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del grupo',
            }),
            'permissions': SelectMultiple(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'name': 'Nombre del Grupo',
            'permissions': 'Permisos',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['modulos'].initial = Modulo.objects.filter(
                grupomodulo__grupo=self.instance
            )


class ModuloForm(ModelForm):
    class Meta:
        model = Modulo
        fields = ['nombre', 'descripcion', 'url', 'icono', 'tipo', 'activo', 'orden']
        widgets = {
            'nombre': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del módulo',
            }),
            'descripcion': Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del módulo',
            }),
            'url': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL del módulo',
            }),
            'icono': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Clase del icono (ej: fas fa-home)',
            }),
            'tipo': Select(attrs={
                'class': 'form-control',
            }),
            'activo': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'orden': NumberInput(attrs={
                'class': 'form-control',
            }),
        }


class TipoModuloForm(ModelForm):
    class Meta:
        model = TipoModulo
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del tipo',
            }),
            'descripcion': Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del tipo de módulo',
            }),
        }