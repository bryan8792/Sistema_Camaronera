from django import forms
from .models import TransferenciaLarva


class TransferenciaLarvaForm(forms.ModelForm):

    class Meta:
        model = TransferenciaLarva
        fields = '__all__'
        widgets = {
            'fecha_larva_sembrada': forms.DateInput(attrs={'type': 'date'}),
            'fecha_siembra_piscina': forms.DateInput(attrs={'type': 'date'}),
        }