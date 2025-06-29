from app_notaCredito.models import CreditNote
from app_venta.models import Sale
from django import forms
from .models import *


class CreditNoteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sale'].queryset = Sale.objects.none()

    class Meta:
        model = CreditNote
        fields = '__all__'
        widgets = {
            'sale': forms.Select(attrs={'class': 'custom-select select2'}),
            'motive': forms.Textarea(attrs={
                'placeholder': 'Ingrese un motivo',
                'class': 'form-control',
                'autocomplete': 'off',
                'rows': 3,
                'cols': 3,
            }),
            'voucher_number_full': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'date_joined': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined'
            }),
            'create_electronic_invoice': forms.CheckboxInput(attrs={
                'class': 'form-control-checkbox',
            }),
            'subtotal_0': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'disabled': True
            }),
            'subtotal_12': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'disabled': True
            }),
            'iva': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'disabled': True
            }),
            'total_iva': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'disabled': True
            }),
            'total_dscto': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'total': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'cash': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'change': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
        }