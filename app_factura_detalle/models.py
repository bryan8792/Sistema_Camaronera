
from django.db import models
from datetime import datetime
from django.db import models
from django.forms import model_to_dict
from app_empresa.app_reg_empresa.models import Empresa
from app_inventario.app_categoria.models import Producto
# Create your models here.
from app_stock.app_detalle_stock.models import Producto_Stock


class Factura(models.Model):
    nombre_prod = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name='Producto ')
    nombre_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa ')
    stock = models.DecimalField(verbose_name='Stock', max_digits=9, decimal_places=2, default=0)
    tipo = models.CharField(max_length=8, default="INGRESO ", null=True, blank=True)
    piscinas = models.CharField(max_length=250, default="Insumo para todas las piscinas ", null=True, blank=True)
    cantidad_usar = models.DecimalField(verbose_name='Cantidad en ', max_digits=9, decimal_places=2, default=0)
    cantidad_ingreso = models.DecimalField(verbose_name='Cantidad de Ingreso en ', max_digits=9, decimal_places=2, default=0)
    cantidad_egreso = models.DecimalField(verbose_name='Cantidad de Egreso en ', max_digits=9, decimal_places=2, default=0)
    fecha_ingreso = models.DateField(default=datetime.now, null=True, blank=True, verbose_name='Fecha de Registro ')
    numero_guia = models.CharField(max_length=250, verbose_name='Numero Guia o Descripción ', null=True, blank=True)
    responsable_ingreso = models.CharField(max_length=250, verbose_name='Persona Responsable ', null=True, blank=True)

    def __str__(self):
        return self.nombre_prod.nombre

    def toJSON(self):
        item = model_to_dict(self)
        item['nombre_prod'] = self.nombre_prod.toJSON()
        item['nombre_empresa'] = self.nombre_empresa.toJSON()
        # item['iva'] = format(self.iva, '.2f')
        # item['total'] = format(self.total, '.2f')
        # item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        # item['det'] = [i.toJSON() for i in self.detsale_set.all()]
        return item

    # def delete(self, using=None, keep_parents=False):
    #     for det in Producto_Stock.objects.all():
    #         det.producto_empresa.stock -= det.cantidad_ingreso
    #         det.producto_empresa.save()
    #     super(Factura, self).delete()

    class Meta:
        db_table = 'tb_det_factura'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['id']