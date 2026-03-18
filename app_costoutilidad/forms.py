from django.forms import ModelForm, TextInput, Textarea
from django.conf.global_settings import DATE_INPUT_FORMATS
from django.db.models import DateField
from django.forms import *
from django.forms.widgets import DateTimeBaseInput
from app_empresa.app_reg_empresa.models import Empresa
from django.conf.global_settings import DATE_INPUT_FORMATS
from django.db.models import DateField
from app_costoutilidad.models import TipoCosto, CostoOperativo, Ciclo, Produccion


class TipoCostoForm(ModelForm):
    class Meta:
        model = TipoCosto
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del tipo de costo'}),
            'descripcion': Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Ingrese una descripción', 'rows': 3}),
        }

class CostoOperativoForm(ModelForm):
    class Meta:
        model = CostoOperativo
        fields = ['piscina', 'tipo_costo', 'fecha', 'monto', 'descripcion', 'comprobante', 'proveedor']
        widgets = {
            'piscina': Select(attrs={'class': 'form-control select2'}),
            'tipo_costo': Select(attrs={'class': 'form-control select2'}),
            'fecha': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monto': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'descripcion': Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comprobante': TextInput(attrs={'class': 'form-control'}),
            'proveedor': Select(attrs={'class': 'form-control select2'}),
        }


class CicloForm(ModelForm):
    class Meta:
        model = Ciclo
        fields = ['piscina', 'nombre', 'fecha_inicio', 'fecha_fin', 'densidad_siembra', 'cantidad_larvas',
                  'activo']
        widgets = {
            'piscina': Select(attrs={'class': 'form-control select2'}),
            'nombre': TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': False}),
            'densidad_siembra': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'cantidad_larvas': NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'activo': CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProduccionForm(ModelForm):
    class Meta:
        model = Produccion
        fields = ['piscina', 'ciclo', 'fecha_cosecha', 'cantidad_kg', 'precio_venta_kg', 'talla_promedio',
                  'cliente', 'factura', 'observaciones']
        widgets = {
            'piscina': Select(attrs={'class': 'form-control select2'}),
            'ciclo': Select(attrs={'class': 'form-control select2'}),
            'fecha_cosecha': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cantidad_kg': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'precio_venta_kg': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'talla_promedio': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'cliente': TextInput(attrs={'class': 'form-control'}),
            'factura': TextInput(attrs={'class': 'form-control'}),
            'observaciones': Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar ciclos activos
        self.fields['ciclo'].queryset = Ciclo.objects.filter(activo=True)

        # Si ya hay una piscina seleccionada, filtrar ciclos por esa piscina
        if 'piscina' in self.data:
            try:
                piscina_id = int(self.data.get('piscina'))
                self.fields['ciclo'].queryset = Ciclo.objects.filter(piscina_id=piscina_id, activo=True)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.piscina:
            self.fields['ciclo'].queryset = Ciclo.objects.filter(piscina=self.instance.piscina, activo=True)