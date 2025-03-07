from crum import get_current_user
from django.db import models
from django.forms import model_to_dict
# Create your models here.
from Sistema_Camaronera.settings import MEDIA_URL, STATIC_URL
# from app_auditoria.models import BaseModel
from app_empresa.app_reg_empresa.models import Empresa
from django.db import connection


class Categoria(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    descripcion = models.CharField(max_length=400, verbose_name='Descripcion')

    def __str__(self):
        return self.nombre

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     user = get_current_user()
    #     if user is not None:
    #         if not self.pk:
    #             self.user_creador = user
    #         else:
    #             self.user_actualizo = user
    #     super(Categoria,self).save()

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        db_table = 'tb_categoria'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['id']


class Producto(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre ', unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    gramaje = models.CharField(max_length=100, verbose_name='Gramaje ', null=True, blank=True)
    descripcion = models.CharField(max_length=400, verbose_name='Sub-Categoria ', null=True, blank=True)
    presentacion = models.CharField(max_length=400, verbose_name='Presentacion ', null=True, blank=True)
    peso_presentacion = models.DecimalField(max_digits=19, decimal_places=0, verbose_name='Peso de la Presentacion ', null=True, blank=True)
    unid_medida = models.CharField(max_length=400, verbose_name='Unidad de Medida de la Presentación ', null=True, blank=True)
    unid_aplicacion = models.CharField(max_length=400, verbose_name='Aplicación en ', null=True, blank=True)
    minimo_stock = models.DecimalField(max_digits=19, decimal_places=0, verbose_name='Stock Mínimo ', null=True, blank=True)
    costo = models.DecimalField(max_digits=19, decimal_places=10, default=0.0000, verbose_name='Valor de Producto ')
    costo_aplicacion = models.DecimalField(max_digits=19, decimal_places=10, default=0.0000, verbose_name='Costo de Aplicacion del Producto ')
    estado = models.BooleanField(default=True, verbose_name='Estado ')
    aplic_directa = models.BooleanField(default=False, verbose_name='Aplicación Directa ')
    imagen = models.ImageField(upload_to='product/%Y/%m/%d', null=True, blank=True, verbose_name='Seleccionar Imagen ')

    def __str__(self):
        return self.nombre

    def get_unidad_aplicacion(self):
        if self.unid_aplicacion == 'GR':
            return 1000
        elif self.unid_aplicacion == 'KG':
            return 2.2
        elif self.unid_aplicacion == 'LB':
            return 1
        elif self.unid_aplicacion == 'CA':
            return 1
        return 1000

    def get_image(self):
        if self.imagen:
            return '{}{}'.format(MEDIA_URL, self.imagen)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    def toJSON(self):
        item = model_to_dict(self)
        item['valor_aplicacion'] = self.get_unidad_aplicacion()
        item['categoria'] = self.categoria.toJSON()
        item['imagen'] = self.get_image()
        item['minimo_stock'] = '0.00' if self.minimo_stock is None else format(self.minimo_stock, '.2f')
        item['peso_presentacion'] = '0.00' if self.peso_presentacion is None else format(self.peso_presentacion, '.2f')
        item['costo'] = format(self.costo, '.2f')
        item['costo_aplicacion'] = format(self.costo_aplicacion, '.10f')
        return item

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        nuevo_producto = super(Producto, self).save()

        empresas = Empresa.objects.filter(estado=True)
        cursor = connection.cursor()

        for empresa in empresas:
            # Validar si el producto-empresa ya existe
            cursor.execute(
                "SELECT nombre_empresa_id, nombre_prod_id FROM stock_total WHERE nombre_empresa_id = %s AND nombre_prod_id = %s;" % (
                empresa.pk, self.id))
            registros = cursor.fetchall()

            if not registros:
                cursor.execute(
                    "INSERT INTO stock_total (nombre_empresa_id, nombre_prod_id, stock) VALUES (%s, %s, 0);" % (
                    empresa.pk, self.id))

        return nuevo_producto

    class Meta:
        db_table = 'tb_producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['id']
