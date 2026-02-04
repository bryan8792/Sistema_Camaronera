from django import forms
from .models import Retention

class RetentionForm(forms.ModelForm):
    class Meta:
        model = Retention
        fields = ['company', 'client', 'sale']
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control select2'}),
            'client': forms.Select(attrs={'class': 'form-control select2'}),
            'sale': forms.Select(attrs={'class': 'form-control select2'}),
        }
