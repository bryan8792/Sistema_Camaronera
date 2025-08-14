from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import File, Folder, SharedLink, FolderPermission, FilePermission
import os

User = get_user_model()


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'file', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del archivo (opcional)'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '*/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del archivo (opcional)'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class MultipleFileUploadForm(forms.Form):
    """Formulario para subida múltiple - manejado por JavaScript"""
    folder = forms.ModelChoiceField(
        queryset=Folder.objects.none(),
        required=False,
        empty_label="Carpeta Raíz",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Carpeta de Destino'
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Descripción opcional para los archivos...'
        }),
        label='Descripción'
    )
    is_public = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Hacer archivos públicos'
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['folder'].queryset = Folder.objects.filter(owner=user)


class FolderCreateForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa el nombre de la carpeta',
                'maxlength': 255
            }),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional para tu carpeta...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        # Remove invalid characters for folder names
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in name:
                raise forms.ValidationError(f'El nombre de la carpeta no puede contener "{char}"')
        return name

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['parent'].queryset = Folder.objects.filter(owner=user)
            self.fields['parent'].empty_label = "Carpeta raíz"


# <CHANGE> Corregido para usar 'is_public' en lugar de 'visibility'
class FolderEditForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 255
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class FileEditForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 255
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class FolderPermissionForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccionar usuario"
    )

    class Meta:
        model = FolderPermission
        fields = ['user', 'permission_level']
        widgets = {
            'permission_level': forms.Select(attrs={'class': 'form-control'})
        }


class FilePermissionForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autocomplete': 'off'
        }),
        label='Usuario'
    )
    permission_level = forms.ChoiceField(
        choices=FilePermission.PERMISSION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Nivel de Permiso'
    )


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar archivos y carpetas...'
        })
    )
    file_type = forms.ChoiceField(
        choices=[
            ('', 'Todos los tipos'),
            ('image', 'Imágenes'),
            ('document', 'Documentos'),
            ('video', 'Videos'),
            ('audio', 'Audio'),
            ('archive', 'Archivos comprimidos'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


# <CHANGE> Corregido para usar 'is_public' en lugar de 'visibility'
class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'description', 'is_public', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la carpeta'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Only show folders that the user owns as potential parents
            self.fields['parent'].queryset = Folder.objects.filter(owner=user)

        # Make parent field optional
        self.fields['parent'].required = False
        self.fields['parent'].empty_label = "Sin carpeta padre (Raíz)"

