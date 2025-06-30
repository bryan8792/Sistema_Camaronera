from datetime import datetime

from django.db import models
from django.forms import model_to_dict

from app_inventario.app_categoria.models import Producto
from app_proveedor.models import Proveedor
from utilities.choices import *


# Create your models here.
class Purchase(models.Model):
    number = models.CharField(max_length=8, unique=True, verbose_name='Número de factura')
    provider = models.ForeignKey(Proveedor, on_delete=models.PROTECT, verbose_name='Proveedor')
    payment_type = models.CharField(choices=PAYMENT_TYPE, max_length=50, default=PAYMENT_TYPE[0][0], verbose_name='Tipo de pago')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    end_credit = models.DateField(default=datetime.now, verbose_name='Fecha de plazo de credito')
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.provider.nombre_com

    def calculate_invoice(self):
        subtotal = 0.00
        for i in self.purchasedetail_set.all():
            subtotal += float(i.price) * int(i.cant)
        self.subtotal = subtotal
        self.save()

    def delete(self, using=None, keep_parents=False):
        try:
            for i in self.purchasedetail_set.all():
                i.product.stock -= i.cant
                i.product.save()
                i.delete()
        except:
            pass
        super(Purchase, self).delete()

    def toJSON(self):
        item = model_to_dict(self)
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['end_credit'] = self.end_credit.strftime('%Y-%m-%d')
        item['provider'] = self.provider.toJSON()
        item['payment_type'] = {'id': self.payment_type, 'name': self.get_payment_type_display()}
        item['subtotal'] = float(self.subtotal)
        return item

    class Meta:
        db_table = 'tb_compra'
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['id']


class PurchaseDetail(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT)
    product = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cant = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.product.nombre

    def toJSON(self):
        item = model_to_dict(self, exclude=['purchase'])
        item['product'] = self.product.toJSON()
        item['price'] = float(self.price)
        item['dscto'] = float(self.dscto)
        item['subtotal'] = float(self.subtotal)
        return item

    class Meta:
        db_table = 'tb_detCompra'
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalle de Compras'
        ordering = ['id']