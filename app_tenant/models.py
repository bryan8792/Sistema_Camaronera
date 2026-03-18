from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Scheme(TenantMixin):
    """Esquema/Tenant en PostgreSQL"""
    name = models.CharField(max_length=100, verbose_name='Nombre')
    created_on = models.DateField(auto_now_add=True)
    auto_create_schema = True

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Esquema'
        verbose_name_plural = 'Esquemas'


class Domain(DomainMixin):
    """Dominios/Subdominios para cada tenant"""
    pass