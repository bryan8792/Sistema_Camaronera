import base64
import mimetypes
import math
import tempfile
import time
import unicodedata
from io import BytesIO
from xml.etree import ElementTree
from django.db import models
from datetime import datetime
from django.forms import model_to_dict
from Sistema_Camaronera.settings import MEDIA_URL, STATIC_URL, BASE_DIR
from app_proveedor.models import *
from utilities.choices import *
from utilities import printer
from utilities.sri import SRI
import barcode
from barcode import writer
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models import FloatField
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError


class Empresa(models.Model):
    ruc = models.CharField(max_length=13, unique=True, verbose_name='Numero de RUC', null=True, blank=True)
    nombre = models.CharField(max_length=150, verbose_name='Nombre Empresa', unique=True)
    business_name = models.CharField(max_length=50, verbose_name='Razón social', null=True, blank=True)
    tradename = models.CharField(max_length=50, verbose_name='Nombre Comercial', null=True, blank=True)
    direccion = models.CharField(max_length=150, verbose_name='Direccion ', null=True, blank=True)
    main_address = models.CharField(max_length=200, verbose_name='Dirección del Establecimiento Matriz', null=True, blank=True)
    establishment_address = models.CharField(max_length=200, verbose_name='Dirección del Establecimiento Emisor', null=True, blank=True)
    siglas = models.CharField(max_length=150, verbose_name='Siglas ', unique=True)
    establishment_code = models.CharField(max_length=3, verbose_name='Código del Establecimiento Emisor', null=True, blank=True)
    issuing_point_code = models.CharField(max_length=3, verbose_name='Código del Punto de Emisión', null=True, blank=True)
    special_taxpayer = models.CharField(max_length=13, verbose_name='Contribuyente Especial (Número de Resolución)', null=True, blank=True)
    aperturada = models.DateField(default=datetime.now, verbose_name='Fecha de Apertura ', null=True, blank=True)
    actividad = models.CharField(max_length=150, verbose_name='Actividad ', null=True, blank=True)
    estado = models.BooleanField(default=True, verbose_name='Seleccionar el Estado')
    logo = models.ImageField(upload_to='logo_comp/%Y/%m/%d', null=True, blank=True, verbose_name='Logotipo de la empresa')
    obligated_accounting = models.CharField(max_length=2, choices=OBLIGATED_ACCOUNTING, default=OBLIGATED_ACCOUNTING[1][0], verbose_name='Obligado a Llevar Contabilidad')
    environment_type = models.PositiveIntegerField(choices=ENVIRONMENT_TYPE, default=1, verbose_name='Tipo de Ambiente')
    emission_type = models.PositiveIntegerField(choices=EMISSION_TYPE, default=1, verbose_name='Tipo de Emisión')
    retention_agent = models.CharField(max_length=2, choices=RETENTION_AGENT, default=RETENTION_AGENT[1][0], verbose_name='Agente de Retención')
    mobile = models.CharField(max_length=10, verbose_name='Teléfono celular', null=True, blank=True)
    phone = models.CharField(max_length=9, verbose_name='Teléfono convencional', null=True, blank=True)
    email = models.CharField(max_length=50, verbose_name='Email', null=True, blank=True)
    website = models.CharField(max_length=250, verbose_name='Dirección de página web', null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')
    iva = models.DecimalField(default=0.00, decimal_places=2, max_digits=9, verbose_name='IVA')
    vat_percentage = models.IntegerField(choices=VAT_PERCENTAGE, default=VAT_PERCENTAGE[3][0], verbose_name='Porcentaje del IVA')
    electronic_signature = models.FileField(null=True, blank=True, upload_to='company/%Y/%m/%d', verbose_name='Firma electrónica (Archivo P12)')
    electronic_signature_key = models.CharField(max_length=100, verbose_name='Clave de firma electrónica', null=True, blank=True)
    email_host = models.CharField(max_length=30, default='smtp.gmail.com', verbose_name='Servidor de correo', null=True, blank=True)
    email_port = models.IntegerField(default=587, verbose_name='Puerto del servidor de correo', null=True, blank=True)
    email_host_user = models.CharField(max_length=100, verbose_name='Username del servidor de correo', null=True, blank=True)
    email_host_password = models.CharField(max_length=30, verbose_name='Password del servidor de correo', null=True, blank=True)

    def __str__(self):
        return self.nombre

    def get_image(self):
        if self.logo:
            return '{}{}'.format(MEDIA_URL, self.logo)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    def get_full_path_image(self):
        if self.logo:
            return self.logo.path
        return f'{BASE_DIR}{STATIC_URL}img/empty.png'

    def get_iva(self):
        return float(self.iva)

    def get_electronic_signature(self):
        if self.electronic_signature:
            return f'{MEDIA_URL}{self.electronic_signature}'
        return None

    def get_logo_base64(self):
        if not self.logo:
            return None

        mime, _ = mimetypes.guess_type(self.logo.path)

        with open(self.logo.path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')

        return f'data:{mime};base64,{encoded}'

    def toJSON(self):
        item = model_to_dict(self)
        item['logo'] = self.get_image()
        item['aperturada'] = self.aperturada.strftime('%Y-%m-%d')
        item['electronic_signature'] = self.get_electronic_signature()
        item['iva'] = float(self.iva)
        return item

    class Meta:
        db_table = 'tb_empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['id']


class Piscinas(models.Model):
    orden = models.CharField(max_length=150, unique=True, verbose_name='Orden de las Piscinas ')
    numero = models.CharField(max_length=150, unique=True, verbose_name='Número de Piscina ')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa ")
    hect = models.CharField(max_length=150, verbose_name='Hectáreas de Dimensiones')
    pis = models.BooleanField(default=True, verbose_name="Piscina ")
    prec = models.BooleanField(default=False, verbose_name="Precria ")
    estado = models.BooleanField(default=True, verbose_name="Estado ")
    inventoried = models.BooleanField(default=True, verbose_name='¿Es inventariado?')
    with_tax = models.BooleanField(default=True, verbose_name='¿Se cobra impuesto?')
    plan_cuenta = models.ForeignKey(
        'app_contabilidad_planCuentas.PlanCuenta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='piscinas',
        verbose_name='Plan de Cuentas'
    )

    cuenta_suministros = models.ForeignKey(
        'app_contabilidad_planCuentas.PlanCuenta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='piscinas_suministros',
        verbose_name='Cuenta de Suministros'
    )

    def __str__(self):
        return self.numero

    def clean(self):
        if self.pis and self.prec:
            raise ValidationError("No puede ser Piscina y Precría al mismo tiempo.")
        if not self.pis and not self.prec:
            raise ValidationError("Debe seleccionar Piscina o Precría.")

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None

        if not es_nuevo:
            anterior = Piscinas.objects.get(pk=self.pk)

        super().save(*args, **kwargs)

        if es_nuevo:
            PiscinaHistorial.objects.create(
                piscina=self,
                fue_piscina=self.pis,
                fue_precria=self.prec
            )
        else:
            if anterior.pis != self.pis or anterior.prec != self.prec:
                PiscinaHistorial.objects.filter(
                    piscina=self,
                    fecha_fin__isnull=True
                ).update(fecha_fin=timezone.now())

                PiscinaHistorial.objects.create(
                    piscina=self,
                    fue_piscina=self.pis,
                    fue_precria=self.prec
                )

    def get_area_hectareas(self):
        try:
            return float(str(self.hect).replace(",", "."))
        except:
            return 0.0

    def toJSON(self):
        item = model_to_dict(self)
        item['empresa'] = self.empresa.toJSON()
        item['plan_cuenta'] = self.plan_cuenta.toJSON() if self.plan_cuenta else None
        item['cuenta_suministros'] = self.cuenta_suministros.toJSON() if self.cuenta_suministros else None
        return item

    class Meta:
        db_table = 'tb_piscina'
        verbose_name = 'Piscina'
        verbose_name_plural = 'Piscinas'
        ordering = ['id']



class PiscinaHistorial(models.Model):
    piscina = models.ForeignKey(
        'Piscinas',
        on_delete=models.CASCADE,
        related_name='historial'
    )

    fue_piscina = models.BooleanField(default=False)
    fue_precria = models.BooleanField(default=False)

    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tb_piscina_historial'
        ordering = ['-fecha_inicio']

    def __str__(self):
        if self.fue_piscina:
            return f'{self.piscina} - Piscina'
        return f'{self.piscina} - Precría'


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
    proveedor = models.ForeignKey('app_proveedor.Proveedor', on_delete=models.CASCADE, related_name='costos_operativos')
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
