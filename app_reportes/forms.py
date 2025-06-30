from django import forms
from app_contabilidad_planCuentas.models import Recibo
from app_inventario.app_categoria.models import Producto


class ReportForm(forms.Form):
    date_range = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }), label='Buscar por rango de fechas')

    sale = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }), label='Venta')

    product = forms.ModelChoiceField(widget=forms.SelectMultiple(attrs={
        'class': 'form-control select2',
    }), queryset=Producto.objects.all(), label='Producto')

    receipt = forms.ModelChoiceField(widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }), queryset=Recibo.objects.all().order_by('id'), label='Comprobante')