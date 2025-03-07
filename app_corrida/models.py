
from django.db import models
from datetime import datetime
from django.forms import model_to_dict
from app_empresa.app_reg_empresa.models import Piscinas
from app_inventario.app_categoria.models import Producto


class PrecSiembraEnc(models.Model):
    fecha_registro = models.DateField(default=datetime.now, null=True, blank=True, verbose_name='Fecha de Registro ')
    fecha_compra = models.DateField(default=datetime.now, null=True, blank=True, verbose_name='Fecha de Compra ')
    fecha_transferencia = models.DateField(default=datetime.now, null=True, blank=True, verbose_name='Fecha de Transferencia')
    observacion = models.CharField(max_length=550, verbose_name='Observación', null=True, blank=True, default="Sin Novedades, Ninguna Observación")
    prod_cantidad = models.TextField(verbose_name='Prod Cantidad', null=True, blank=True)
    resul_oper = models.TextField(verbose_name='Resultado Proceso', null=True, blank=True)
    tot_comp = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    tip_precSiembra = models.BooleanField(default=True)
    # empresa
    # nombre = models.CharField(max_length=150, verbose_name='Nombre Empresa ', unique=True)

    def __str__(self):
        return self.observacion

    def toJSON(self):
        item = model_to_dict(self)
        item['number'] = f'{self.id:06d}'
        item['fecha_registro'] = self.fecha_registro
        item['fecha_compra'] = self.fecha_compra
        item['fecha_transferencia'] = self.fecha_transferencia
        return item

    class Meta:
        db_table = 'db_prec_siembra_enc'
        verbose_name = 'Precria Siembra Enc'
        verbose_name_plural = 'Precrias Siembras Enc'
        ordering = ['id']


class PrecSiembraCuerp(models.Model):
    fecha_registro = models.ForeignKey(PrecSiembraEnc, on_delete=models.CASCADE)
    fecha_compra = models.DateField(default=datetime.now, null=True, blank=True, verbose_name='Fecha de Compra ')
    fecha_transferencia = models.DateField(default=datetime.now, null=True, blank=True, verbose_name='Fecha de Transferencia ')
    comp_1 = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    comp_2 = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    comp_3 = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    tot_comp = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    prod_cantidad = models.TextField(verbose_name='Prod Cantidad', null=True, blank=True)
    piscina = models.ForeignKey(Piscinas, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=True)
    dias = models.IntegerField(default=0)
    siembra = models.DecimalField(default=0.000, max_digits=9, decimal_places=3)
    costo_larva = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    dia_por_hect = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    prod_cantidad_proceso = models.TextField(verbose_name='Cantidad Prod Proceso', null=True, blank=True)
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    resul_oper = models.TextField(verbose_name='Resultado Proceso', null=True, blank=True)
    observacion = models.CharField(max_length=550, verbose_name='Observación', null=True, blank=True, default="Sin Novedades, Ninguna Observación")

    def __str__(self):
        return self.piscina

    def toJSON(self):
        item = model_to_dict(self)
        item['fecha_registro'] = self.fecha_registro.toJSON()
        item['fecha_compra'] = self.fecha_compra
        item['fecha_transferencia'] = self.fecha_transferencia
        return item

    class Meta:
        db_table = 'db_prec_siembra_cuerp'
        verbose_name = 'Precria Siembra Cuerpo'
        verbose_name_plural = 'Precrias Siembras Cuerpo'
        ordering = ['id']