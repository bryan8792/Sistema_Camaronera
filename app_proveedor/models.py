
from django.db import models
from django.forms import model_to_dict
from app_contabilidad_planCuentas.models import PlanCuenta
# Create your models here.

class Proveedor(models.Model):
    ruc = models.CharField(max_length=13, unique=True, verbose_name='RUC ')
    razon_soc = models.CharField(max_length=250, verbose_name='Razon Social ', unique=True)
    nombre_com = models.CharField(max_length=400, verbose_name='Nombre Comercial ', null=True, blank=True)
    actividad_com = models.CharField(max_length=350, verbose_name='Actividad Comercial ', null=True, blank=True)
    cod_contable = models.ForeignKey(PlanCuenta, on_delete=models.CASCADE, null=True, blank=True)
    grupo = models.CharField(max_length=50, verbose_name='Grupo ')
    telef1 = models.CharField(max_length=10, verbose_name='Telefono 1 ', null=True, blank=True)
    telef2 = models.CharField(max_length=10, verbose_name='Telefono 2 ', null=True, blank=True)
    mail = models.TextField(verbose_name='Correo ', null=True, blank=True)
    direccion1 = models.CharField(max_length=350, verbose_name='Direccion 1 ', null=True, blank=True)
    direccion2 = models.CharField(max_length=350, verbose_name='Direccion 2 ', null=True, blank=True)
    direccion3 = models.CharField(max_length=350, verbose_name='Direccion 3 ', null=True, blank=True)
    ciudad = models.CharField(max_length=50, verbose_name='Ciudad ', null=True, blank=True)
    estado = models.CharField(max_length=50, default=True, verbose_name='Estado ')

    def __str__(self):
        return self.nombre_com

    def toJSON(self):
        item = model_to_dict(self)
        item['cod_contable'] = self.cod_contable.toJSON() if self.cod_contable else None
        return item

    class Meta:
        db_table = 'tb_proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['id']