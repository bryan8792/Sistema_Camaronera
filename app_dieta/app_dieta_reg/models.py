import decimal
from Sistema_Camaronera.settings import MEDIA_URL, STATIC_URL
from datetime import datetime
from django.db import models, transaction
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


from django.db import models, transaction
from django.forms import model_to_dict
from crum import get_current_user

class DetalleDiaDieta(models.Model):
    dieta = models.ForeignKey('DiaDietaRegistro', on_delete=models.CASCADE)
    piscinas = models.ForeignKey(
        Piscinas,
        on_delete=models.CASCADE,
        verbose_name='Empresa',
        null=True,
        blank=True
    )
    balanceado = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
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
        return str(self.dieta)

    # ======================================================
    # SAVE → CREA / EDITA (ERP CONTROLADO)
    # ======================================================
    def save(self, *args, **kwargs):

        with transaction.atomic():

            es_edicion = self.pk is not None

            # --------------------------------------------------
            # 1. SI ES EDICIÓN → REVERSAR EGRESOS ANTERIORES
            # --------------------------------------------------
            if es_edicion:
                movimientos = Producto_Stock.objects.select_for_update().filter(
                    detalle_dieta_id=self.pk,
                    tipo='EGRESO',
                    activo=True
                )

                for mov in movimientos:
                    stock = mov.producto_empresa
                    stock.stock += mov.cantidad_egreso
                    stock.save(update_fields=['stock'])

                    mov.activo = False
                    mov.save(update_fields=['activo'])

            # --------------------------------------------------
            # 2. GUARDAR DETALLE
            # --------------------------------------------------
            super().save(*args, **kwargs)

            # Validaciones mínimas
            if not self.piscinas:
                return

            empresa = self.piscinas.empresa
            fecha = self.dieta.fecha
            usuario = get_current_user() or '-'

            # --------------------------------------------------
            # 3. EGRESO DE BALANCEADO
            # --------------------------------------------------
            if self.balanceado and self.cantidad > 0:
                try:
                    ps = Total_Stock.objects.select_for_update().get(
                        nombre_empresa=empresa,
                        nombre_prod=self.balanceado
                    )

                    Producto_Stock.objects.create(
                        producto_empresa=ps,
                        tipo='EGRESO',
                        piscinas=self.piscinas,
                        cantidad_egreso=self.cantidad,
                        fecha_ingreso=fecha,
                        numero_guia='CONSUMO DE DIETA',
                        responsable_ingreso=usuario,
                        detalle_dieta_id=self.pk
                    )

                except Total_Stock.DoesNotExist:
                    pass

            # --------------------------------------------------
            # 4. EGRESO DE INSUMOS
            # --------------------------------------------------
            insumos = (
                (self.insumo1, self.gramaje1),
                (self.insumo2, self.gramaje2),
                (self.insumo3, self.gramaje3),
                (self.insumo4, self.gramaje4),
            )

            for insumo_id, gramaje in insumos:
                if insumo_id and gramaje > 0:
                    try:
                        ps = Total_Stock.objects.select_for_update().get(
                            nombre_empresa=empresa,
                            nombre_prod_id=int(insumo_id)
                        )

                        Producto_Stock.objects.create(
                            producto_empresa=ps,
                            tipo='EGRESO',
                            piscinas=self.piscinas,
                            cantidad_egreso=gramaje,
                            fecha_ingreso=fecha,
                            numero_guia='CONSUMO DE DIETA',
                            responsable_ingreso=usuario,
                            detalle_dieta_id=self.pk
                        )

                    except Total_Stock.DoesNotExist:
                        pass

    # ======================================================
    # DELETE → REVERSA STOCK + DESACTIVA KARDEX
    # ======================================================
    def delete(self, using=None, keep_parents=False):

        with transaction.atomic():

            movimientos = Producto_Stock.objects.select_for_update().filter(
                detalle_dieta_id=self.pk,
                tipo='EGRESO',
                activo=True
            )

            for mov in movimientos:
                stock = mov.producto_empresa
                stock.stock += mov.cantidad_egreso
                stock.save(update_fields=['stock'])

                mov.activo = False
                mov.save(update_fields=['activo'])

            super().delete(using=using, keep_parents=keep_parents)

    # ======================================================
    # SERIALIZACIÓN
    # ======================================================
    def toJSON(self):
        item = model_to_dict(self)
        item['piscinas'] = self.piscinas.toJSON() if self.piscinas else None
        item['balanceado'] = self.balanceado.toJSON() if self.balanceado else None
        item['cantidad'] = format(self.cantidad, '.0f')
        for i in range(1, 5):
            item[f'insumo{i}'] = format(getattr(self, f'insumo{i}'), '.0f')
            item[f'gramaje{i}'] = format(getattr(self, f'gramaje{i}'), '.2f')

        return item

    class Meta:
        db_table = 'db_dia_dieta_detalle'
        verbose_name = "Detalle del día dieta"
        verbose_name_plural = "Detalle del día dietas"
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
