from django import forms
from .models import Anticipo, FormaPago, TipoPago, FormaPagoOpcion

class AnticipoForm(forms.ModelForm):
    class Meta:
        model = Anticipo
        fields = ['caja', 'tipo', 'centro_costo', 'tipo_identificacion', 'identificacion',
                  'razon_social', 'nombre_comercial', 'telefono', 'celular', 'email',
                  'ciudad', 'direccion', 'fecha', 'monto', 'concepto', 'categoria_contable']
        widgets = {
            'caja': forms.Select(attrs={'class': 'form-control select2'}),
            'tipo': forms.Select(attrs={'class': 'form-control select2'}),
            'centro_costo': forms.Select(attrs={'class': 'form-control select2'}),
            'tipo_identificacion': forms.Select(attrs={'class': 'form-control select2'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese identificación'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razón social'}),
            'nombre_comercial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre comercial'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Celular'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'placeholder': '0.00'}),
            'concepto': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Concepto del anticipo'}),
            'categoria_contable': forms.Select(attrs={'class': 'form-control select2'}),
        }
        labels = {
            'caja': 'Caja',
            'tipo': 'Tipo',
            'centro_costo': 'Centro de Costo',
            'tipo_identificacion': 'Tipo Ident.',
            'identificacion': 'Identificación',
            'razon_social': 'Razón social',
            'nombre_comercial': 'Nombre comercial',
            'telefono': 'Teléfono',
            'celular': 'Celular',
            'email': 'Email',
            'ciudad': 'Ciudad',
            'direccion': 'Dirección',
            'fecha': 'Fecha',
            'monto': 'Monto',
            'concepto': 'Concepto',
            'categoria_contable': 'Categoría contable',
        }

class TipoPagoForm(forms.ModelForm):
    class Meta:
        model = TipoPago
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: CONTADO, CREDITO'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }

class FormaPagoOpcionForm(forms.ModelForm):
    class Meta:
        model = FormaPagoOpcion
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: EFECTIVO, CHEQUE'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }
