
from django.db import models
from datetime import datetime
from django.forms import model_to_dict
from app_empresa.app_reg_empresa.models import Empresa
from app_inventario.app_categoria.models import Producto
from tkinter import *
# Create your models here.
from app_proveedor.models import Proveedor
from app_user.models import User


class Total_Stock(models.Model):
    nombre_prod = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name='Producto')
    nombre_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa')
    stock = models.DecimalField(verbose_name='Stock', max_digits=9, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre_prod.nombre

    def toJSON(self):
        item = model_to_dict(self)
        item['nombre_prod'] = self.nombre_prod.toJSON()
        item['nombre_empresa'] = self.nombre_empresa.toJSON()
        item['stock'] = format(self.stock, '.2f')
        return item

    class Meta:
        db_table = 'stock_total'
        verbose_name = 'Stock Total'
        verbose_name_plural = 'Stocks Totales'
        ordering = ['id']



class InvoiceStock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    fecha_ingreso = models.DateField(default=datetime.now, null=True, blank=True, verbose_name='Fecha de Registro ')
    numero_guia = models.CharField(max_length=250, verbose_name='Numero Factura, Guia o Descripción ', null=True, blank=True)
    responsable_ingreso = models.CharField(max_length=250, verbose_name='Persona Responsable ', null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, verbose_name='Proveedor ', null=True, blank=True)
    observacion = models.TextField(default="Sin Novedades", null=True, blank=True, verbose_name='Observación ')
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2, verbose_name='Subtotal ')
    iva = models.DecimalField(default=0.00, max_digits=9, decimal_places=2, verbose_name='IVA ')
    ivacalc = models.DecimalField(default=0.00, max_digits=9, decimal_places=2, verbose_name='IVA Calc ')
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2, verbose_name='Total ')

    def __str__(self):
        return self.user.get_full_name()

    def toJSON(self):
        item = model_to_dict(self)
        item['number'] = f'{self.id:06d}'
        item['user'] = self.user.toJSON()
        item['proveedor'] = self.proveedor.toJSON()
        item['date_creation'] = self.date_creation.strftime('%Y-%m-%d')
        item['fecha_ingreso'] = self.fecha_ingreso.strftime('%Y-%m-%d')
        item['subtotal'] = format(self.subtotal, '.2f')
        item['iva'] = format(self.iva, '.2f')
        item['ivacalc'] = format(self.ivacalc, '.2f')
        item['total'] = format(self.total, '.2f')
        item['det'] = [i.toJSON() for i in self.producto_stock_set.all()]
        return item

    def delete(self, using=None, keep_parents=False):
        for det in self.producto_stock_set.all():
            det.producto_empresa.stock = float(det.producto_empresa.stock) - float(det.cantidad_ingreso)
            det.producto_empresa.save()
        super(InvoiceStock, self).delete()

    class Meta:
        db_table = 'invoiceStock'
        verbose_name = 'InvoiceStock'
        verbose_name_plural = 'InvoiceStock'
        ordering = ['id']



class Producto_Stock(models.Model):
    invoice_stock = models.ForeignKey(InvoiceStock, on_delete=models.CASCADE, verbose_name='Factura', null=True, blank=True)
    producto_empresa = models.ForeignKey(Total_Stock, on_delete=models.CASCADE, verbose_name='Producto Stock ')
    tipo = models.CharField(max_length=8, default="INGRESO", null=True, blank=True)
    piscinas = models.CharField(max_length=250, default="Todas las Piscinas", null=True, blank=True)
    cantidad_usar = models.DecimalField(verbose_name='Cantidad en ', max_digits=9, decimal_places=2, default=0)
    cantidad_ingreso = models.DecimalField(verbose_name='Cantidad de Ingreso en ', max_digits=9, decimal_places=2, default=0)
    cantidad_egreso = models.DecimalField(verbose_name='Cantidad de Egreso en ', max_digits=9, decimal_places=2, default=0)
    fecha_ingreso = models.DateField(default=datetime.now, null=True, blank=True, verbose_name='Fecha de Registro ')
    numero_guia = models.CharField(max_length=250, verbose_name='Numero Guia o Descripción ', null=True, blank=True)
    responsable_ingreso = models.CharField(max_length=250, verbose_name='Persona Responsable ', null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, verbose_name='Proveedor ', null=True, blank=True)
    observacion = models.TextField(default="Sin Novedades", null=True, blank=True, verbose_name='Observación ')
    activo = models.BooleanField(default=True, verbose_name='Registro Activo ')
    detalle_dieta_id = models.IntegerField(null=True, blank=True, verbose_name='Id Detalle Dieta ')
    subtotal = models.DecimalField(verbose_name='Subtotal ', max_digits=9, decimal_places=2, default=0.00, null=True, blank=True)
    iva = models.DecimalField(verbose_name='IVA ', max_digits=9, decimal_places=2, default=0.00, null=True, blank=True)
    ivacalc = models.DecimalField(verbose_name='IVA Calc ', max_digits=9, decimal_places=2, default=0.00, null=True, blank=True)
    total = models.DecimalField( verbose_name='Total ', max_digits=9, decimal_places=2, default=0.00, null=True, blank=True)

    def __str__(self):
        return self.producto_empresa.nombre_empresa.siglas

    def toJSON(self):
        item = model_to_dict(self)
        item['producto_empresa'] = self.producto_empresa.toJSON()
        item['cantidad_usar'] = format(self.cantidad_usar, '.2f')
        item['cantidad_ingreso'] = format(self.cantidad_ingreso, '.2f')
        item['cantidad_egreso'] = format(self.cantidad_egreso, '.2f')
        item['subtotal'] = format(self.subtotal, '.2f')
        item['iva'] = format(self.iva, '.2f')
        item['ivacalc'] = format(self.ivacalc, '.2f')
        item['total'] = format(self.total, '.2f')
        return item

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.tipo == 'INGRESO':
            self.producto_empresa.stock = float(self.producto_empresa.stock) + float(self.cantidad_ingreso)
        else:
            self.producto_empresa.stock = float(self.producto_empresa.stock) - float(self.cantidad_egreso)
        self.producto_empresa.save()

        # Poner por defecto activo = True cuando se cree el registro
        if not self.pk:
            self.activo = True

        super(Producto_Stock, self).save()

    class Meta:
        db_table = 'stock_prod'
        verbose_name = 'Kardex'
        verbose_name_plural = 'Kardexs'
        ordering = ['fecha_ingreso', '-piscinas']



# class detProducto_Stock(models.Model):
#     tot_stock = models.ForeignKey(Total_Stock, on_delete=models.CASCADE)
#     prod_stock = models.ForeignKey(Producto_Stock, on_delete=models.CASCADE)
#     fecha_ingreso = models.DateField(default=datetime.now, null=True, blank=True, verbose_name='Fecha de Registro ')
#     numero_guia = models.CharField(max_length=250, verbose_name='Numero Guia o Descripción ', null=True, blank=True)
#     responsable_ingreso = models.CharField(max_length=250, verbose_name='Persona Responsable ', null=True, blank=True)
#
#     def __str__(self):
#         return self.tot_stock.nombre_empresa.siglas
#
#     def toJSON(self):
#         item = model_to_dict(self)
#         item['tot_stock'] = self.tot_stock.toJSON()
#         item['prod_stock'] = self.prod_stock.toJSON()
#         return item
#
#     class Meta:
#         db_table = 'detProd_Stock'
#         verbose_name = 'Prod Stock'
#         verbose_name_plural = 'Prod Stocks'
#         ordering = ['id']
