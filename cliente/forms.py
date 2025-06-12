# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Cliente

class ClienteUserForm(forms.ModelForm):
    # Campos del modelo User (no relacionados directamente con Cliente)
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'})
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )

    class Meta:
        model = Cliente
        fields = ['first_name', 'last_name', 'cedula', 'movil', 'nacimiento', 'direccion', 'identification_type', 'send_email_invoice']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula o RUC'}),
            'movil': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'identification_type': forms.Select(attrs={'class': 'form-control'}),
            'send_email_invoice': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        # Creamos el User primero
        user = User.objects.create(
            username=f'user_{self.cleaned_data["cedula"]}',
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        # Creamos el Cliente y lo asociamos al User
        cliente = super().save(commit=False)
        cliente.usuario = user
        if commit:
            cliente.save()
        return cliente
