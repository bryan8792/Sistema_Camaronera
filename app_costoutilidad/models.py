from django.db import models
from django.forms import model_to_dict
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models import FloatField
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal

from app_empresa.app_piscinas.models import Piscinas
from app_proveedor.models import Proveedor


# Create your models here.
class TipoCosto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')

    def __str__(self):
        return self.nombre

    def toJSON(self):
        return model_to_dict(self)

    class Meta:
        db_table = 'tb_tipo_costo'
        verbose_name = 'Tipo de Costo'
        verbose_name_plural = 'Tipos de Costos'
        ordering = ['nombre']


class CostoOperativo(models.Model):
    piscina = models.ForeignKey(Piscinas, on_delete=models.CASCADE, related_name='costos', verbose_name='Piscina')
    tipo_costo = models.ForeignKey(TipoCosto, on_delete=models.PROTECT, related_name='costos', verbose_name='Tipo de Costo')
    fecha = models.DateField(verbose_name='Fecha')
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    comprobante = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número de factura o comprobante')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='costos_operativos')
    usuario_registro = models.CharField(max_length=100, blank=True, null=True, verbose_name='Usuario que registra')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')

    def __str__(self):
        return f"{self.piscina} - {self.tipo_costo} - ${self.monto}"

    def toJSON(self):
        item = model_to_dict(self)
        item['piscina'] = self.piscina.toJSON()
        item['proveedor'] = self.proveedor.toJSON()
        item['tipo_costo'] = self.tipo_costo.toJSON()
        item['fecha'] = self.fecha.strftime('%Y-%m-%d')
        item['monto'] = float(self.monto)
        item['fecha_registro'] = self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
        return item

    class Meta:
        db_table = 'tb_costo_operativo'
        verbose_name = 'Costo Operativo'
        verbose_name_plural = 'Costos Operativos'
        ordering = ['-fecha', 'piscina']


class Ciclo(models.Model):
    piscina = models.ForeignKey(Piscinas, on_delete=models.CASCADE, related_name='ciclos', verbose_name='Piscina')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_fin = models.DateField(blank=True, null=True, verbose_name='Fecha de fin')
    densidad_siembra = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Densidad de siembra (larvas/m²)')
    cantidad_larvas = models.IntegerField(blank=True, null=True, verbose_name='Cantidad de larvas')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    def __str__(self):
        return f"{self.piscina} - {self.nombre}"

    def toJSON(self):
        item = model_to_dict(self)
        item['piscina'] = self.piscina.toJSON()
        item['fecha_inicio'] = self.fecha_inicio.strftime('%Y-%m-%d')
        if self.fecha_fin:
            item['fecha_fin'] = self.fecha_fin.strftime('%Y-%m-%d')
        item['densidad_siembra'] = float(self.densidad_siembra) if self.densidad_siembra else None
        return item

    class Meta:
        db_table = 'tb_ciclo'
        verbose_name = 'Ciclo'
        verbose_name_plural = 'Ciclos'
        ordering = ['-fecha_inicio']


class Produccion(models.Model):
    piscina = models.ForeignKey(Piscinas, on_delete=models.CASCADE, related_name='producciones', verbose_name='Piscina')
    ciclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE, related_name='producciones', blank=True, null=True, verbose_name='Ciclo')
    fecha_cosecha = models.DateField(verbose_name='Fecha de cosecha')
    cantidad_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Cantidad en kilogramos')
    precio_venta_kg = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Precio de venta por kilogramo')
    talla_promedio = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Talla promedio en gramos')
    cliente = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cliente')
    factura = models.CharField(max_length=50, blank=True, null=True, verbose_name='Factura')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    usuario_registro = models.CharField(max_length=100, blank=True, null=True, verbose_name='Usuario que registra')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')

    def __str__(self):
        return f"{self.piscina} - {self.fecha_cosecha} - {self.cantidad_kg}kg"

    @property
    def valor_total(self):
        return self.cantidad_kg * self.precio_venta_kg

    def toJSON(self):
        item = model_to_dict(self)
        item['piscina'] = self.piscina.toJSON()
        if self.ciclo:
            item['ciclo'] = self.ciclo.toJSON()
        item['fecha_cosecha'] = self.fecha_cosecha.strftime('%Y-%m-%d')
        item['cantidad_kg'] = float(self.cantidad_kg)
        item['precio_venta_kg'] = float(self.precio_venta_kg)
        item['talla_promedio'] = float(self.talla_promedio) if self.talla_promedio else None
        item['valor_total'] = float(self.valor_total)
        item['fecha_registro'] = self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
        return item

    class Meta:
        db_table = 'tb_produccion'
        verbose_name = 'Producción'
        verbose_name_plural = 'Producciones'
        ordering = ['-fecha_cosecha']


class CostoUtilidadHectarea:

    @staticmethod
    def calcular_por_piscina(piscina_id, fecha_inicio, fecha_fin):
        try:
            piscina = Piscinas.objects.get(id=piscina_id)
            hectareas = piscina.get_area_hectareas()

            if hectareas <= 0:
                return {'error': f"La piscina {piscina.numero} no tiene un área válida en hectáreas"}

        except Piscinas.DoesNotExist:
            return {'error': "Piscina no encontrada"}

        costos = CostoOperativo.objects.filter(
            piscina_id=piscina_id,
            fecha__range=[fecha_inicio, fecha_fin]
        ).aggregate(
            total=Coalesce(Sum('monto'), Decimal('0'))
        )['total']

        producciones = Produccion.objects.filter(
            piscina_id=piscina_id,
            fecha_cosecha__range=[fecha_inicio, fecha_fin]
        )

        ingresos = sum(p.cantidad_kg * p.precio_venta_kg for p in producciones)

        utilidad = ingresos - costos

        return {
            'id': piscina.id,
            'piscina': piscina.numero,
            'empresa': piscina.empresa.siglas,
            'hectareas': hectareas,
            'costos_totales': float(costos),
            'ingresos_totales': float(ingresos),
            'utilidad_total': float(utilidad),
            'costo_por_hectarea': float(costos) / hectareas if hectareas > 0 else 0,
            'ingreso_por_hectarea': float(ingresos) / hectareas if hectareas > 0 else 0,
            'utilidad_por_hectarea': float(utilidad) / hectareas if hectareas > 0 else 0,
            'rentabilidad': (float(utilidad) / float(costos) * 100) if costos > 0 else 0,
        }

    @staticmethod
    def calcular_todas_piscinas(fecha_inicio, fecha_fin, empresa_id=None):

        query = Piscinas.objects.filter(estado=True)
        if empresa_id:
            query = query.filter(empresa_id=empresa_id)

        piscinas = query.order_by('numero')

        resultados = []
        totales = {
            'hectareas': 0,
            'costos_totales': 0,
            'ingresos_totales': 0,
            'utilidad_total': 0,
        }

        for piscina in piscinas:
            resultado = CostoUtilidadHectarea.calcular_por_piscina(
                piscina.id, fecha_inicio, fecha_fin
            )

            if 'error' not in resultado:
                resultados.append(resultado)

                totales['hectareas'] += resultado['hectareas']
                totales['costos_totales'] += resultado['costos_totales']
                totales['ingresos_totales'] += resultado['ingresos_totales']
                totales['utilidad_total'] += resultado['utilidad_total']

        return {
            'resultados': resultados,
            'totales': totales
        }
