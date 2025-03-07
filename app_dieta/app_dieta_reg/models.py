import decimal
from Sistema_Camaronera.settings import MEDIA_URL, STATIC_URL
from datetime import datetime
from django.db import models
from django.forms import model_to_dict
from app_empresa.app_reg_empresa.models import Piscinas, Empresa
from app_inventario.app_categoria.models import Producto
# Create your models here.
from app_stock.app_detalle_stock.models import Total_Stock, Producto_Stock
from crum import get_current_user
from django.db import connection


class AnioDieta(models.Model):
    anio_dieta = models.IntegerField(verbose_name='Ingresar Año', null=True, blank=True)

    def __str__(self):
        return str(self.anio_dieta)

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        db_table = 'db_anio_dieta'
        verbose_name = 'AnioDieta'
        verbose_name_plural = "1. Años Dieta"
        ordering = ['id']


class MesDieta(models.Model):
    anio = models.ForeignKey(AnioDieta, on_delete=models.CASCADE, null=True, blank=True)
    mes_dieta = models.CharField(max_length=250, verbose_name='Mes de Dieta', null=True, blank=True)
    descripcion = models.CharField(max_length=250, verbose_name='Descripción', null=True, blank=True)

    def __str__(self):
        return self.mes_dieta

    def toJSON(self):
        item = model_to_dict(self)
        item['anio'] = self.anio.toJSON()
        return item

    class Meta:
        db_table = 'db_mes_dieta'
        verbose_name = 'MesDieta'
        verbose_name_plural = '2. Meses Dietas'
        ordering = ['id']


class DiaDietaRegistro(models.Model):
    mes_dieta = models.ForeignKey(MesDieta, on_delete=models.CASCADE, verbose_name="Mes de Dieta")
    fecha = models.DateField(verbose_name='Fecha Dieta', null=True, blank=True)
    tip_dieta = models.BooleanField(default=True, verbose_name='Si es Dieta de Piscinas Seleccione ')

    def __str__(self):
        return "%s" % (self.fecha)

    def toJSON(self):
        item = model_to_dict(self)
        item['mes_dieta'] = self.mes_dieta.toJSON()
        item['det'] = [i.toJSON() for i in self.detallediadieta_set.all()]
        return item

    class Meta:
        db_table = 'db_dia_dieta_reg'
        verbose_name = 'DiaDietaRegistro'
        verbose_name_plural = '3. Dias de Dietas Registros'
        ordering = ['fecha']


class DetalleDiaDieta(models.Model):
    dieta = models.ForeignKey(DiaDietaRegistro, on_delete=models.CASCADE)
    piscinas = models.ForeignKey(Piscinas, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=True)
    balanceado = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    insumo1 = models.IntegerField(default=0)
    gramaje1 = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    insumo2 = models.IntegerField(default=0)
    gramaje2 = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    insumo3 = models.IntegerField(default=0)
    gramaje3 = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    insumo4 = models.IntegerField(default=0)
    gramaje4 = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    def __str__(self):
        return self.dieta

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            nuevo_detalle = super(DetalleDiaDieta, self).save()
            usuario_actual = '-'
            user = get_current_user()

            if user is not None:
                usuario_actual = user
            # Actualizar stock para producto
            ps = Total_Stock.objects.get(nombre_empresa_id=self.piscinas.empresa.pk, nombre_prod_id=self.balanceado.pk)
            print(ps)
            if ps:
                # Registrar egreso #
                producto = Producto_Stock()
                producto.producto_empresa_id = ps.pk
                producto.tipo = 'EGRESO'
                producto.piscinas = self.piscinas
                producto.cantidad_egreso = float(self.cantidad)
                producto.fecha_ingreso = self.dieta.fecha
                producto.numero_guia = 'CONSUMO DE DIETA'
                producto.responsable_ingreso = usuario_actual
                producto.detalle_dieta_id = self.pk
                producto.save()

            # Actualizar stock para insumo
            datos = [(self.insumo1, self.gramaje1), (self.insumo2, self.gramaje2), (self.insumo3, self.gramaje3), (self.insumo4, self.gramaje4)]
            print(datos)
            for d in datos:
                if d[0]:
                    ps = Total_Stock.objects.get(nombre_empresa_id=self.piscinas.empresa.pk, nombre_prod_id=int(d[0]))
                    if ps:
                        # Registrar egreso
                        producto = Producto_Stock()
                        producto.producto_empresa_id = ps.pk
                        producto.tipo = 'EGRESO'
                        producto.piscinas = self.piscinas
                        producto.cantidad_egreso = float(d[1])
                        producto.fecha_ingreso = self.dieta.fecha
                        producto.numero_guia = 'CONSUMO DE DIETA'
                        producto.responsable_ingreso = usuario_actual
                        producto.detalle_dieta_id = self.pk
                        producto.save()

            return nuevo_detalle
        except Exception as exc:
            pass

    def delete(self, using=None, keep_parents=False):
        cursor = connection.cursor()
        sql = 'UPDATE stock_prod SET activo = FALSE where detalle_dieta_id = %s;' % self.pk
        cursor.execute(sql)
        super(DetalleDiaDieta, self).delete()


    def toJSON(self):
        item = model_to_dict(self)
        item['piscinas'] = self.piscinas.toJSON()
        item['balanceado'] = self.balanceado.toJSON()
        item['cantidad'] = format(self.cantidad, '.0f')
        item['insumo1'] = format(self.insumo1, '.0f')
        item['gramaje1'] = format(self.gramaje1, '.0f')
        item['insumo2'] = format(self.insumo2, '.0f')
        item['gramaje2'] = format(self.gramaje2, '.0f')
        item['insumo3'] = format(self.insumo3, '.0f')
        item['gramaje3'] = format(self.gramaje3, '.0f')
        item['insumo4'] = format(self.insumo4, '.0f')
        item['gramaje4'] = format(self.gramaje4, '.0f')
        return item

    class Meta:
        db_table = 'db_dia_dieta_detalle'
        verbose_name = "4. Detalle del dia dieta"
        verbose_name_plural = "4. Detalle del dia dietas"
        ordering = ['id']


class DescripcionDieta(models.Model):
    fecha = models.DateField(default=datetime.now, verbose_name='Fecha de Escaneo ', null=True, blank=True)
    descripcion = models.CharField(max_length=400, verbose_name='Novedad de la Dieta ')
    imagen = models.ImageField(upload_to='descripcionDieta/%Y/%m/%d', null=True, blank=True, verbose_name='Archivo Escaneado ')

    def __str__(self):
        return self.descripcion

    def get_image(self):
        if self.imagen:
            return '{}{}'.format(MEDIA_URL, self.imagen)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    def toJSON(self):
        item = model_to_dict(self)
        item['imagen'] = self.get_image()
        return item

    class Meta:
        db_table = 'tb_registro'
        verbose_name = 'Registro'
        verbose_name_plural = 'Registros'
        ordering = ['id']
