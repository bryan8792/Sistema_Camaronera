# Create your models here.
import math
import os
import re
import unicodedata
import traceback
from datetime import datetime
from django.utils.timezone import now
from Sistema_Camaronera import settings
from django.db import models
from django.db.models import FloatField
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.forms import model_to_dict
from django.db import connection
import unicodedata
from django.core.files.base import ContentFile
import xml.etree.ElementTree as ET
import xml.dom.minidom
import barcode
from barcode import writer
from django.contrib.contenttypes.models import ContentType
from utilities.choices import *
from xml.etree.ElementTree import Element, SubElement, tostring
from utilities import printer
from utilities.sri import SRI
from datetime import datetime
from django.core.files.base import ContentFile
import base64
import tempfile
from io import BytesIO
from django.core.files import File
import time
from django.core.validators import MinValueValidator, MaxValueValidator


class Cuenta_Prueba(models.Model):
    nombre = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50, unique=True)  # Código de la cuenta
    descripcion = models.TextField(blank=True, null=True)
    cuenta_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subcuentas',
        blank=True,
        null=True
    )
    es_activo = models.BooleanField(default=True)  # Si la cuenta está activa o no

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def obtener_cuentas_hijas(self):
        """Obtiene todas las subcuentas directas"""
        return self.subcuentas.all()

    def obtener_todas_subcuentas(self):
        """Obtiene todas las subcuentas en un árbol de manera recursiva"""
        subcuentas = []
        for subcuenta in self.subcuentas.all():
            subcuentas.append(subcuenta)
            subcuentas.extend(subcuenta.obtener_todas_subcuentas())
        return subcuentas

    class Meta:
        db_table = 'Cuenta'
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"


class Folder(models.Model):
    name = models.CharField(max_length=128)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        db_table = 'tb_Carpeta'
        verbose_name = "Carpeta"
        verbose_name_plural = "Carpetas"


class PlanCuenta(models.Model):
    codigo = models.CharField(max_length=50, default=0)
    nombre = models.CharField(max_length=150, verbose_name='Nombre de la Cuenta')
    nivel = models.SmallIntegerField(default=1)
    tipo_cuenta = models.CharField(max_length=150, verbose_name='Tipo de Cuenta')
    estado = models.BooleanField(default=True, verbose_name='Estado ')
    band_deudor = models.BooleanField(default=False)
    band_total = models.BooleanField(default=False, verbose_name='Cuenta de Total')
    band_valida = models.BooleanField(default=False)
    band_gastoDistribuido = models.BooleanField(default=False)
    empresa = models.ForeignKey('app_reg_empresa.Empresa', on_delete=models.CASCADE, verbose_name="Empresa ", null=True, blank=True)
    periodo = models.CharField(max_length=150, verbose_name='Periodo (Año)')
    parentId = models.ForeignKey('self', db_column='idparentId', null=True, blank=True, on_delete=models.CASCADE,
                                 related_name='idparentId', verbose_name='Cuenta Raiz o Cuenta Padre')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return '{} /  {} /  Nivel: {} / Empresa: {} '.format(self.codigo, self.nombre, self.nivel, self.empresa)

    def get_name(self):
        return '{} {}'.format(self.codigo, self.nombre)

    def code_parent(self):
        return '' if self.parentId is None else self.parentId.codigo

    def get_full_hierarchy(self):
        """
        Construye la jerarquía completa de la cuenta actual hasta la raíz.
        """
        hierarchy = []
        current_account = self

        while current_account is not None:
            hierarchy.insert(0, f"{current_account.codigo} - {current_account.nombre}")
            current_account = current_account.parentId

        return " → ".join(hierarchy)

    def toJSON(self):
        item = model_to_dict(self)
        item['id'] = self.id
        item['empresa'] = self.empresa.toJSON()
        item['full_name'] = '{} / {}'.format(self.codigo, self.nombre)
        item['full_name_2'] = '{} /  {} /  Nivel: {}'.format(self.codigo, self.nombre, self.nivel)
        item['full_name_total'] = '{} /  {} /  Nivel: {} / Empresa: {} '.format(self.codigo, self.nombre, self.nivel, self.empresa)
        item['cuenta_padre'] = '{} '.format(self.parentId)
        item['cuenta_padre2'] = '{} '.format(self.parentId)
        item['jerarquia_completa'] = self.get_full_hierarchy()
        item['get_name'] = self.get_name()
        item['parentId'] = self.parentId.id if self.parentId else None
        return item

    class Meta:
        db_table = 'tb_planCuenta'
        verbose_name = 'Plan Cuenta'
        verbose_name_plural = 'Planes Cuentas'
        ordering = ['codigo']


class EncabezadoCuentasPlanCuenta(models.Model):
    codigo = models.IntegerField(default=0)
    tip_cuenta = models.CharField(max_length=150, verbose_name='Tipo de Cuenta', null=True, blank=True)
    tip_transa = models.CharField(max_length=150, verbose_name='Tipo de Transacción', null=True, blank=True)
    fecha = models.DateField(verbose_name='Fecha', null=True, blank=True)
    comprobante = models.CharField(max_length=400, verbose_name='Comprobante', null=True, blank=True)
    descripcion = models.CharField(max_length=400, verbose_name='Descripción', null=True, blank=True)
    direccion = models.TextField(default="Ingrese una Direccion", null=True, blank=True, verbose_name='Dirección')
    ruc = models.CharField(max_length=400, verbose_name='RUC', null=True, blank=True)
    reg_ats = models.CharField(max_length=400, verbose_name='Es ATS', default='SIN REGISTRO DE ATS')
    empresa = models.ForeignKey('app_reg_empresa.Empresa', on_delete=models.CASCADE, verbose_name="Seleccionar Empresa:")
    reg_control = models.CharField(max_length=400, verbose_name='Tipo de Registro', default='RT')
    proveedor = models.ForeignKey('app_proveedor.Proveedor', on_delete=models.PROTECT, verbose_name="Seleccionar Proveedor ",
                                  null=True, blank=True)

    def __str__(self):
        return str(self.codigo)

    # def __str__(self):
    #     return str(self.comprobante) if self.comprobante else "Sin comprobante"
        # return str(self.fecha) if self.fecha else 'Sin fecha'

    def toJSON(self):
        item = model_to_dict(self)
        item['empresa'] = self.empresa.toJSON()
        item['proveedor'] = self.proveedor.toJSON() if self.proveedor else None
        item['det'] = [i.toJSON() for i in self.detallecuentasplancuenta_set.all()]
        item['detATS'] = [ats.toJSON() for ats in self.anexotransaccional_set.all()]
        return item

    class Meta:
        db_table = 'tb_encabezadocuentasplanCuenta'
        verbose_name = 'tb_encabezadocuentaplanCuenta'
        verbose_name_plural = 'tb_encabezadocuentasplanCuenta'
        ordering = ['id']


class DetalleCuentasPlanCuenta(models.Model):
    encabezadocuentaplan = models.ForeignKey(EncabezadoCuentasPlanCuenta, on_delete=models.CASCADE, null=True, blank=True)
    cheque = models.CharField(max_length=400, verbose_name='Cheque', null=True, blank=True)
    band_integridad = models.SmallIntegerField(default=0)
    orden = models.SmallIntegerField(default=0)
    band_niif = models.BooleanField(default=False)
    band_importacion = models.BooleanField(default=True)
    cuenta = models.ForeignKey(PlanCuenta, on_delete=models.CASCADE, null=True, blank=True)
    origen = models.CharField(max_length=90, null=True, blank=True)
    detalle = models.CharField(max_length=150, verbose_name='Detalle', null=True, blank=True, default="")
    deducible = models.DecimalField(default=0.00, max_digits=19, decimal_places=2)
    debe = models.DecimalField(default=0.00, max_digits=19, decimal_places=2)
    haber = models.DecimalField(default=0.00, max_digits=19, decimal_places=2)

    # conc_banc_num = models.IntegerField(default=0)
    # conc_banc_det = models.CharField(max_length=400, verbose_name='Conciliación Bancaria')
    # flujo_efec = models.CharField(max_length=400, verbose_name='Flujo Efectivo')
    # tipo_mov = models.CharField(max_length=400, verbose_name='Tipo Movimiento')
    # sustento = models.CharField(max_length=400, verbose_name='Sustento')
    # tipo_indic = models.CharField(max_length=400, verbose_name='Tipo Indicador')
    # tipo_cli = models.CharField(max_length=400, verbose_name='Tipo Cliente')
    # cta_super = models.IntegerField(default=0, verbose_name='Cuenta Super')
    # flujo_super = models.CharField(max_length=400, verbose_name='Flujo Super')
    # form_cientuno = models.IntegerField(default=0, verbose_name='Formulario 101')
    # estado = models.BooleanField(default=True, verbose_name='Estado ')

    def __str__(self):
        return str(self.encabezadocuentaplan)

    def get_full_hierarchy(self):
        """
        Construye la jerarquía completa desde la cuenta actual hasta la raíz.
        """
        hierarchy = []
        current_account = self.cuenta

        while current_account is not None:
            hierarchy.insert(0, f"{current_account.codigo} - {current_account.nombre}")  # Insertar al principio
            current_account = current_account.parentId

        return " → ".join(hierarchy)  # Formato: Padre → Subnivel → Hijo

    def toJSON(self):
        item = model_to_dict(self)
        item['codigo_asiento_transaccion'] = self.encabezadocuentaplan.codigo
        item['fecha_asiento_transaccion'] = self.encabezadocuentaplan.fecha
        item['nombre_asiento_transaccion'] = self.encabezadocuentaplan.tip_cuenta
        item['codigo_cuenta_plan'] = format(self.cuenta.codigo)
        item['nombre_cuenta_plan'] = self.cuenta.nombre
        item['cuenta'] = self.cuenta.toJSON()
        item['jerarquia_completa'] = self.get_full_hierarchy()
        item['deducible'] = format(self.deducible, '.2f')
        item['debe'] = format(self.debe, '.2f')
        item['haber'] = format(self.haber, '.2f')
        return item

    def get_saldos(self, fecha_inicio, fecha_fin):
        """
        Calcula los saldos para un período específico
        """
        saldo_anterior = DetalleCuentasPlanCuenta.objects.filter(
            cuenta=self.cuenta,
            encabezadocuentaplan__fecha__lt=fecha_inicio
        ).aggregate(
            debe=Coalesce(Sum('debe'), 0),
            haber=Coalesce(Sum('haber'), 0)
        )

        saldo_mes = DetalleCuentasPlanCuenta.objects.filter(
            cuenta=self.cuenta,
            encabezadocuentaplan__fecha__range=[fecha_inicio, fecha_fin]
        ).aggregate(
            debe=Coalesce(Sum('debe'), 0),
            haber=Coalesce(Sum('haber'), 0)
        )

        return {
            'saldo_anterior': {
                'debe': float(saldo_anterior['debe']),
                'haber': float(saldo_anterior['haber'])
            },
            'saldo_mes': {
                'debe': float(saldo_mes['debe']),
                'haber': float(saldo_mes['haber'])
            },
            'saldo_actual': {
                'debe': float(saldo_anterior['debe'] + saldo_mes['debe']),
                'haber': float(saldo_anterior['haber'] + saldo_mes['haber'])
            }
        }

    class Meta:
        db_table = 'tb_detallecuentasplanCuenta'
        verbose_name = 'tb_detallecuentaplanCuenta'
        verbose_name_plural = 'tb_detallecuentasplanCuenta'
        ordering = ['id']


class Recibo(models.Model):
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPE, verbose_name='Tipo de Comprobante')
    establishment_code = models.CharField(max_length=3, verbose_name='Código del Establecimiento Emisor')
    issuing_point_code = models.CharField(max_length=3, verbose_name='Código del Punto de Emisión')
    sequence = models.PositiveIntegerField(default=0, verbose_name='Secuencia actual')
    empresa = models.ForeignKey('app_reg_empresa.Empresa', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'

    @property
    def name(self):
        return self.get_voucher_type_display()

    def get_name_xml(self):
        return self.remove_accents(self.name.replace(' ', '_').lower())

    def remove_accents(self, text):
        return ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))

    def get_sequence(self):
        return f'{self.sequence:09d}'

    def toJSON(self):
        item = model_to_dict(self)
        item['name'] = self.name
        item['empresa'] = self.empresa.toJSON() if self.empresa else None
        item['voucher_type'] = {'id': self.voucher_type, 'name': self.get_voucher_type_display()}
        return item

    class Meta:
        db_table = 'tb_recibo'
        verbose_name = 'Recibo'
        verbose_name_plural = 'Recibos'


class AnexoTransaccional(models.Model):
    # ENCABEZADO DEL ATS
    encabezadocuentaplan = models.ForeignKey(EncabezadoCuentasPlanCuenta, on_delete=models.CASCADE, null=True,
                                             blank=True)
    # detallecuentaplan = models.ForeignKey(DetalleCuentasPlanCuenta, on_delete=models.CASCADE, null=True, blank=True)
    estab = models.CharField(max_length=6, default=000, verbose_name='Establecimiento')
    company = models.ForeignKey('app_reg_empresa.Empresa', on_delete=models.PROTECT, verbose_name='Seleccionar empresa')
    estab_serie = models.CharField(max_length=6, default=000, verbose_name='Establecimiento - Serie')
    # DATOS COMPROBANTE DE VENTA
    receipt = models.ForeignKey(Recibo, on_delete=models.CASCADE, verbose_name='Tipo de comprobante',
                                limit_choices_to={'voucher_type__in': [VOUCHER_TYPE[0][0], VOUCHER_TYPE[-1][0]]})
    comp_numero = models.CharField(max_length=9, verbose_name='Número comprobante', null=True, blank=True)
    comp_numero_full = models.CharField(max_length=20, verbose_name='Número de comprobante completo', null=True,
                                        blank=True)
    comp_fecha = models.DateField(verbose_name='Fecha registro', null=True, blank=True)
    ag_ret = models.CharField(max_length=5, default='Si')
    sust_trib = models.CharField(max_length=500, verbose_name='Sustento Tributario',
                                 default="No existe sustituto tributario")
    tipo_comp = models.CharField(max_length=500, verbose_name='Tipo de Comprobante',
                                 default="No existe tipo de comprobante")
    comp_serie = models.CharField(max_length=6, default=000, verbose_name='N. Serie/Secuencia:')
    comp_secuencia = models.CharField(max_length=9, default=000)
    comp_fecha_reg = models.DateField(verbose_name='Fecha Reg. Contable', null=True, blank=True)
    comp_fecha_em = models.DateField(verbose_name='Fecha de Emisión', null=True, blank=True)
    n_autoriz = models.CharField(max_length=500, verbose_name='Numero de Autorización', default="No existe ingreso")
    # PARAMETROS DE VALORES - COMPROBANTE DE VENTA
    base_dif_cero_iva = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                            verbose_name='Base IVA dif 0')
    base_cero = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Base 0%')
    base_iva_normal = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Base IVA Normal')
    base_iva_bienes = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                          verbose_name='IVA Compra Bienes')
    base_no_obj_iva = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Base no Obj IVA')
    base_excent_iva = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                          verbose_name='Base excenta IVA')
    base_ice = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Base ICE')
    porcent_ice = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Porcentaje ICE')
    # FORMULARIO 104 VALOR BRUTO
    base_cero_bruto = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Base 0%')
    base_cero_bruto_fcientocuatro = models.DecimalField(default=0, max_digits=19, decimal_places=0)
    base_iva_normal_bruto = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                                verbose_name='Base IVA Normal')
    base_iva_normal_bruto_fcientocuatro = models.DecimalField(default=0, max_digits=19, decimal_places=0)
    base_iva_bienes_bruto = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                                verbose_name='IVA Compra Bienes')
    base_iva_bienes_bruto_fcientocuatro = models.DecimalField(default=0, max_digits=19, decimal_places=0)
    # FORMULARIO 104 VALOR NETO
    base_cero_neto = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Base 0%')
    base_iva_normal_neto = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                               verbose_name='Base IVA Normal')
    # CANTIDAD DE PORCENTAJE DE IVA
    base_iva_normal_porcen = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                                 verbose_name='Base IVA Normal')
    base_iva_bienes_porcen = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                                 verbose_name='IVA Compra Bienes')
    # MONTOS DE CANTIDADES
    monto_iva_normal = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                           verbose_name='Monto IVA Normal')
    monto_iva_bienes = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                           verbose_name='Monto Compra Bienes')
    monto_ice = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Monto ICE')
    monto_total = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='TOTAL FACT')

    # RETENCION DEL IVA
    ret_serie = models.CharField(max_length=6, default=000, verbose_name='Serie de Retención')
    ret_numero = models.CharField(max_length=9, default=000, verbose_name='Número de Retención')
    ret_numero_full = models.CharField(max_length=20, default=000, verbose_name='Número de retención completo')
    ret_fecha = models.DateField(verbose_name='Fecha Emision Retencion', null=True, blank=True)

    iva_cero = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='IVA 0%')
    ret_iva_cero = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Ret IVA 0%')
    cant_iva_cero = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Cant IVA 0%')

    iva_diez = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='IVA 10%')
    ret_iva_diez = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Ret IVA 10%')
    cant_iva_diez = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Cant IVA 10%')

    iva_veint = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='IVA 20%')
    ret_iva_veint = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Ret IVA 20%')
    cant_iva_veint = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Cant IVA 20%')

    iva_treint = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='IVA 30%')
    ret_iva_treint = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Ret IVA 30%')
    cant_iva_treint = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Cant IVA 30%')

    iva_cinc = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='IVA 50%')
    ret_iva_cinc = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Ret IVA 50%')
    cant_iva_cinc = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Cant IVA 50%')

    iva_setn = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='IVA 70%')
    ret_iva_setn = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Ret IVA 70%')
    cant_iva_setn = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Cant IVA 70%')

    iva_cien = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='IVA 100%')
    ret_iva_cien = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Ret IVA 100%')
    cant_iva_cien = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Cant IVA 100%')

    # RETENCION DE LA FUENTE
    ret_fue_iva_uno = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Base 1')
    ret_fue_iva_cero_uno = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                               verbose_name='Base 1 al 0%')
    ret_fue_iva_anexo_uno = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                                verbose_name='Anexo IVA 1')
    ret_fue_iva_porcent_uno = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                                  verbose_name='Porcentaje 1')
    ret_fue_iva_monto_uno = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Monto 1')
    ret_fue_iva_dos = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Base 2')
    ret_fue_iva_cero_dos = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                               verbose_name='Base 2 al 0%')
    ret_fue_iva_anexo_dos = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                                verbose_name='Anexo IVA 2')
    ret_fue_iva_porcent_dos = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                                  verbose_name='Porcentaje 2')
    ret_fue_iva_monto_dos = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Monto 2')
    ret_fue_iva_tres = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Base 3')
    ret_fue_iva_cero_tres = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                                verbose_name='Base 3 al 0%')
    ret_fue_iva_anexo_tres = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                                 verbose_name='Anexo IVA 3')
    ret_fue_iva_porcent_tres = models.DecimalField(default=0.00, max_digits=19, decimal_places=2,
                                                   verbose_name='Porcentaje 3')
    ret_fue_iva_monto_tres = models.DecimalField(default=0.00, max_digits=19, decimal_places=2, verbose_name='Monto 3')
    # REEMBOLSO
    reem_serie = models.CharField(max_length=6, default=000, verbose_name='Serie de Reembolso')
    reem_numero = models.CharField(max_length=9, default=000, verbose_name='Número de Reembolso')
    reem_numero_full = models.CharField(max_length=20, default=000, verbose_name='Número de reembolso completo')
    reem_fecha = models.DateField(verbose_name='Fecha Emision Reembolso', null=True, blank=True)
    reem_ruc = models.CharField(max_length=13, default=0000000000000, null=True, blank=True,
                                verbose_name='RUC de Reembolso')
    # FORMA DE PAGO
    tip_form = models.CharField(max_length=100, null=True, blank=True, default="", verbose_name='Tipo de Forma de Pago')
    det_form = models.CharField(max_length=100, null=True, blank=True, default="", verbose_name='Detalle Forma de Pago')
    # PROCESOS
    environment_type = models.PositiveIntegerField(choices=ENVIRONMENT_TYPE, default=ENVIRONMENT_TYPE[0][0], null=True,
                                                   blank=True)
    access_code = models.CharField(max_length=49, null=True, blank=True, verbose_name='Clave de acceso')
    xml_authorized = models.FileField(null=True, blank=True, verbose_name='XML Autorizado')
    pdf_authorized = models.FileField(upload_to='pdf_authorized/%Y/%m/%d', null=True, blank=True,
                                      verbose_name='PDF Autorizado')
    create_electronic_document = models.BooleanField(default=True, verbose_name='Crear documento electrónico',
                                                     null=True, blank=True)
    create_electronic_invoice = models.BooleanField(default=True, verbose_name='Crear factura electrónica')
    status = models.CharField(max_length=50, choices=INVOICE_STATUS, default=INVOICE_STATUS[0][0],
                              verbose_name='Estado', null=True, blank=True)

    def __str__(self):
        return self.encabezadocuentaplan

    def get_date_joined(self):
        return (datetime.strptime(self.comp_fecha_reg, '%Y-%m-%d') if isinstance(self.comp_fecha_reg,
                                                                                 str) else self.comp_fecha_reg).strftime(
            '%Y-%m-%d')

    def get_xml_authorized(self):
        if self.xml_authorized:
            return f'{settings.MEDIA_URL}{self.xml_authorized}'
        return None

    def get_pdf_authorized(self):
        if self.pdf_authorized:
            return f'{settings.MEDIA_URL}{self.pdf_authorized}'
        return None

    def get_voucher_number_full(self):
        return f'{self.receipt.establishment_code}-{self.receipt.issuing_point_code}-{self.comp_numero}'

    def generate_voucher_number(self, increase=True):
        if isinstance(self.receipt.sequence, str):
            self.receipt.sequence = int(self.receipt.sequence)
        number = self.receipt.sequence + 1 if increase else self.receipt.sequence
        return f'{number:09d}'


    # DENTRO DE LA FUNCION - SI ponlo asi:
    def generate_voucher_number_full(self):
        if self.receipt_id is None:
            # Import DENTRO de la funcion (lazy import) - esto SI funciona
            from django.db import connection
            from app_empresa.app_reg_empresa.models import Empresa  # <-- AQUI SI

            current_schema = connection.schema_name

            if current_schema and current_schema != 'public':
                self.company = Empresa.objects.filter(schema_name=current_schema).first()
            else:
                self.company = Empresa.objects.first()

            if self.company:
                self.receipt = Recibo.objects.get(
                    voucher_type=VOUCHER_TYPE[0][0],
                    establishment_code=self.company.establishment_code,
                    issuing_point_code=self.company.issuing_point_code
                )
        self.voucher_number = self.generate_voucher_number()
        return self.get_voucher_number_full()

    def generate_pdf_authorized(self):
        sale = AnexoTransaccional.objects.filter(id=self.id).first()
        encabezado = sale.encabezadocuentaplan
        detalle = DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan_id=sale.encabezadocuentaplan_id)
        rv = BytesIO()
        barcode.Code128(sale.access_code,
                        writer=barcode.writer.ImageWriter()).write(rv,
                                                                   options={'text_distance': 3.0,
                                                                            'font_size': 6})
        file = base64.b64encode(rv.getvalue()).decode("ascii")
        context = {'sale': sale, 'encabezado': encabezado, 'height': 450, 'detalle': detalle,
                   'access_code_barcode': f"data:image/png;base64,{file}"}
        pdf_file = printer.create_pdf(context=context, template_name='app_factura_gasto/format/invoice.html')

        with tempfile.NamedTemporaryFile(delete=True) as file_temp:
            file_temp.write(pdf_file)
            file_temp.flush()
            self.pdf_authorized.save(name=f'{self.receipt.get_name_xml()}_{self.access_code}.pdf',
                                     content=File(file_temp))

    def label_tipo_comprobante(self):
        label = ''
        if self.tipo_comp == '1':
            label = 'FACTURA'
        return label

    def generate_electronic_invoice(self):
        try:
            xml_content, access_key = self.generate_xml()
            print('→ XML de retención creado correctamente')
            print(f'→ Clave de acceso: {access_key}')
            result = {'resp': True, 'xml': xml_content}
            # Firmar el XML
            sri = SRI()
            result = sri.firm_xml(instance=self, xml=result['xml'])
            print(f'→ Firmado XML: {result["resp"]}')
            if result['resp']:
                # Validar el XML
                result = sri.validate_xml(instance=self, xml=result['xml'])
                print(f'→ Validado XML: {result["resp"]}')
                if result['resp']:
                    # Autorizar el XML
                    result = sri.authorize_xml(instance=self)
                    print(f'→ Autorización intento 1: {result["resp"]}')
                    # Reintentar hasta 3 veces si falla
                    index = 1
                    while not result['resp'] and index < 3:
                        time.sleep(1)
                        result = sri.authorize_xml(instance=self)
                        print(f'→ Autorización intento {index + 1}: {result["resp"]}')
                        index += 1
                    if result['resp']:
                        # <CHANGE> Solo incrementar secuencia después de autorización exitosa
                        self.receipt.sequence += 1
                        self.receipt.save()
                        print(f'→ Secuencia del recibo incrementada a: {self.receipt.sequence}')

                        result['print_url'] = self.get_pdf_authorized()
                        print(f'→ Comprobante autorizado exitosamente')
                        print(f'→ XML guardado en: {self.get_xml_authorized()}')
                        print(f'→ PDF guardado en: {self.get_pdf_authorized()}')
                    else:
                        print(f'→ Error en autorización después de 3 intentos')
                else:
                    print(f'→ Error en validación del XML')
            else:
                print(f'→ Error al firmar el XML')

        except Exception as e:
            import traceback
            print(f'→ Error al generar comprobante electrónico: {str(e)}')
            print(traceback.format_exc())
            result = {
                'resp': False,
                'error': f'Error al generar comprobante: {str(e)}'
            }

        return result

    def generate_xml(self):
        try:
            # Crear clave de acceso con validación
            access_key = SRI().create_access_key(self)
            print("Clave de acceso generada:", access_key)
            if not access_key:
                raise ValueError("La clave de acceso no fue generada correctamente.")

            # Almacenar access_code en el modelo
            self.access_code = access_key

            # Crear el elemento raíz
            comprobante = ET.Element("comprobanteRetencion", id="comprobante", version="2.0.0")

            # Agregar el encabezado de la factura
            infoTributaria = ET.SubElement(comprobante, "infoTributaria")
            ET.SubElement(infoTributaria, "ambiente").text = str(self.company.environment_type)
            ET.SubElement(infoTributaria, "tipoEmision").text = str(self.company.emission_type)
            ET.SubElement(infoTributaria, "razonSocial").text = self.company.business_name
            ET.SubElement(infoTributaria, "nombreComercial").text = self.company.tradename
            ET.SubElement(infoTributaria, "ruc").text = self.company.ruc
            ET.SubElement(infoTributaria, "claveAcceso").text = access_key
            ET.SubElement(infoTributaria, "codDoc").text = self.receipt.voucher_type
            ET.SubElement(infoTributaria, "estab").text = self.receipt.establishment_code
            ET.SubElement(infoTributaria, "ptoEmi").text = self.receipt.issuing_point_code
            ET.SubElement(infoTributaria, "secuencial").text = self.comp_numero
            ET.SubElement(infoTributaria, "dirMatriz").text = self.company.main_address

            # Agregar la información de la factura
            infoFactura = ET.SubElement(comprobante, "infoCompRetencion")
            ET.SubElement(infoFactura, "fechaEmision").text = datetime.strptime(self.comp_fecha_em,
                                                                                '%Y-%m-%d').strftime(
                '%d/%m/%Y') if isinstance(self.comp_fecha_em, str) else self.comp_fecha_em.strftime('%d/%m/%Y')
            ET.SubElement(infoFactura, "dirEstablecimiento").text = self.company.establishment_address
            ET.SubElement(infoFactura, "obligadoContabilidad").text = self.company.obligated_accounting
            ET.SubElement(infoFactura, "tipoIdentificacionSujetoRetenido").text = "04"
            ET.SubElement(infoFactura, "parteRel").text = "NO"
            ET.SubElement(infoFactura, "razonSocialSujetoRetenido").text = self.encabezadocuentaplan.descripcion
            ET.SubElement(infoFactura, "identificacionSujetoRetenido").text = self.encabezadocuentaplan.ruc
            periodo_fiscal = datetime.strptime(self.comp_fecha_em, '%Y-%m-%d').strftime('%m/%Y') if isinstance(
                self.comp_fecha_em, str) else self.comp_fecha_em.strftime('%m/%Y')
            ET.SubElement(infoFactura, "periodoFiscal").text = periodo_fiscal

            detalles = ET.SubElement(comprobante, "docsSustento")
            detalle = ET.SubElement(detalles, "docSustento")
            ET.SubElement(detalle, "codSustento").text = "02"  # Sustento Tributario
            ET.SubElement(detalle, "codDocSustento").text = "01"  # Tipo Comprobante
            ET.SubElement(detalle, "numDocSustento").text = f'{self.comp_serie}{self.comp_secuencia}'
            ET.SubElement(detalle, "fechaEmisionDocSustento").text = datetime.strptime(self.comp_fecha_em,
                                                                                       "%Y-%m-%d").strftime("%d/%m/%Y")
            ET.SubElement(detalle, "fechaRegistroContable").text = datetime.strptime(self.comp_fecha_reg,
                                                                                     "%Y-%m-%d").strftime("%d/%m/%Y")
            ET.SubElement(detalle, "numAutDocSustento").text = self.n_autoriz
            ET.SubElement(detalle, "pagoLocExt").text = '01'
            total_sin_impuestos = float(self.base_cero) + float(self.base_iva_normal)
            ET.SubElement(detalle, "totalSinImpuestos").text = f'{total_sin_impuestos:.2f}'
            ET.SubElement(detalle, "importeTotal").text = f'{float(self.monto_total):.2f}'

            impuestos = ET.SubElement(detalle, "impuestosDocSustento")
            if float(self.base_iva_normal) > 0:
                impuesto = ET.SubElement(impuestos, "impuestoDocSustento")
                ET.SubElement(impuesto, "codImpuestoDocSustento").text = "2"
                ET.SubElement(impuesto, "codigoPorcentaje").text = "4"  # 15% IVA
                ET.SubElement(impuesto, "baseImponible").text = f'{float(self.base_iva_normal):.2f}'
                ET.SubElement(impuesto, "tarifa").text = "15"
                ET.SubElement(impuesto, "valorImpuesto").text = f'{float(self.monto_iva_normal):.2f}'

            retenciones = ET.SubElement(detalle, "retenciones")
            if float(self.iva_treint) > 0:
                retencion = ET.SubElement(retenciones, "retencion")
                ET.SubElement(retencion, "codigo").text = "2"
                ET.SubElement(retencion, "codigoRetencion").text = "1"
                ET.SubElement(retencion, "baseImponible").text = f'{float(self.iva_treint):.2f}'
                ET.SubElement(retencion, "porcentajeRetener").text = "30"
                ET.SubElement(retencion, "valorRetenido").text = f'{float(self.cant_iva_treint):.2f}'

            if float(self.iva_veint) > 0:
                retencion = ET.SubElement(retenciones, "retencion")
                ET.SubElement(retencion, "codigo").text = "2"
                ET.SubElement(retencion, "codigoRetencion").text = "10"
                ET.SubElement(retencion, "baseImponible").text = f'{float(self.iva_veint):.2f}'
                ET.SubElement(retencion, "porcentajeRetener").text = "20"
                ET.SubElement(retencion, "valorRetenido").text = f'{float(self.cant_iva_veint):.2f}'

            if float(self.iva_cien) > 0:
                retencion = ET.SubElement(retenciones, "retencion")
                ET.SubElement(retencion, "codigo").text = "2"
                ET.SubElement(retencion, "codigoRetencion").text = "2"
                ET.SubElement(retencion, "baseImponible").text = f'{float(self.iva_cien):.2f}'
                ET.SubElement(retencion, "porcentajeRetener").text = "100"
                ET.SubElement(retencion, "valorRetenido").text = f'{float(self.cant_iva_cien):.2f}'

            pagos = ET.SubElement(detalle, "pagos")
            pago = ET.SubElement(pagos, "pago")
            ET.SubElement(pago, "formaPago").text = "20"
            ET.SubElement(pago, "total").text = f'{float(self.monto_total):.2f}'

            # Formatear el XML con sangrías
            xml_string = ET.tostring(comprobante, encoding='unicode')
            print("Contenido XML generado correctamente")

            xml_pretty = xml.dom.minidom.parseString(xml_string).toprettyxml(indent="  ")

            return xml_pretty, access_key

        except Exception as e:
            print("Error en generate_xml:", str(e))
            traceback.print_exc()
            raise

    def is_invoice(self):
        return self.receipt.voucher_type == VOUCHER_TYPE[0][0]

    def toJSON(self):
        item = model_to_dict(self)
        item['receipt'] = self.receipt.toJSON()
        item['comp_fecha'] = self.comp_fecha.strftime('%Y-%m-%d') if self.comp_fecha else None
        item['comp_fecha_reg'] = self.comp_fecha_reg.strftime('%Y-%m-%d')
        item['environment_type'] = {'id': self.environment_type, 'name': self.get_environment_type_display()}
        item['comp_fecha_em'] = '' if self.comp_fecha_em is None else self.comp_fecha_em.strftime('%Y-%m-%d')
        item['xml_authorized'] = self.get_xml_authorized()
        item['pdf_authorized'] = self.get_pdf_authorized()
        return item

    class Meta:
        db_table = 'tb_anexoTransaccional'
        verbose_name = 'tb_anexoTransaccional'
        verbose_name_plural = 'tb_anexosTransaccionales'
        ordering = ['id']


class VoucherErrors(models.Model):
    date_joined = models.DateField(default=now)
    datetime_joined = models.DateTimeField(default=now)
    environment_type = models.PositiveIntegerField(choices=ENVIRONMENT_TYPE, default=ENVIRONMENT_TYPE[0][0])
    reference = models.CharField(max_length=20, null=True, blank=True)
    receipt = models.ForeignKey(Recibo, on_delete=models.CASCADE, null=True, blank=True)
    stage = models.CharField(max_length=20, choices=VOUCHER_STAGE, default=VOUCHER_STAGE[0][0])
    errors = models.JSONField(default=dict)

    def __str__(self):
        return self.stage

    def toJSON(self):
        item = model_to_dict(self)
        # item['receipt'] = self.receipt.toJSON() if self.receipt else None
        item['receipt'] = self.receipt.toJSON()
        item['environment_type'] = {'id': self.environment_type, 'name': self.get_environment_type_display()}
        item['stage'] = {'id': self.stage, 'name': self.get_stage_display()}
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['datetime_joined'] = self.datetime_joined.strftime('%Y-%m-%d %H:%M')
        return item

    class Meta:
        db_table = 'tb_errores_comprobantes'
        verbose_name = 'Errores del Comprobante'
        verbose_name_plural = 'Errores de los Comprobantes'


class ATSConfig(models.Model):
    """Configuración para generación de ATS"""
    id_receptor = models.CharField(max_length=13, verbose_name="ID Receptor")
    nombre_receptor = models.CharField(max_length=200, verbose_name="Nombre Receptor")
    periodicidad_choices = [
        ('mensual', 'Mensual'),
        ('semestral', 'Semestral'),
    ]
    periodicidad = models.CharField(max_length=10, choices=periodicidad_choices, default='mensual')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tb_configATS'
        verbose_name = "Configuración ATS"
        verbose_name_plural = "Configuraciones ATS"

    def __str__(self):
        return f"{self.id_receptor} - {self.nombre_receptor}"


class ATSPeriodo(models.Model):
    """Períodos para generación de ATS"""
    config = models.ForeignKey(ATSConfig, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=20, verbose_name="Período")
    anio = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2050)])
    estado_choices = [
        ('pendiente', 'Pendiente'),
        ('procesado', 'Procesado'),
        ('enviado', 'Enviado'),
    ]
    estado = models.CharField(max_length=10, choices=estado_choices, default='pendiente')
    fecha_generacion = models.DateTimeField(null=True, blank=True)
    archivo_xml = models.FileField(upload_to='ats_xml/', null=True, blank=True)

    def __str__(self):
        return f"{self.periodo} {self.anio} - {self.config.id_receptor}"

    class Meta:
        db_table = 'tb_periodoATS'
        verbose_name = "Período ATS"
        verbose_name_plural = "Períodos ATS"
        unique_together = ['config', 'periodo', 'anio']


class ATSCompra(models.Model):
    """Registro de compras para ATS"""
    periodo = models.ForeignKey(ATSPeriodo, on_delete=models.CASCADE)
    tp_id = models.CharField(max_length=2, verbose_name="TP ID")
    no_identif = models.CharField(max_length=13, verbose_name="No. Identif.")
    proveedor = models.CharField(max_length=200, verbose_name="Proveedor")
    sust_tp = models.CharField(max_length=10, verbose_name="Sust. TP")
    no_doc = models.CharField(max_length=20, verbose_name="# Doc.")
    fecha_emision = models.DateField(verbose_name="F.Emisión")
    valor_objeto_iva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="V.Ito Obj IVA")
    excento = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Excento")
    base_0 = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Base 0%")
    base_iva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Base IVA")
    monto_iva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto IVA")
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total")
    no_retenc = models.CharField(max_length=20, verbose_name="# Retenc.", blank=True)
    rt_iva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="RT IVA", default=0)
    rt_fte = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="RT FTE", default=0)

    def toJSON(self):
        return {
            'id': self.id,
            'tp_id': self.tp_id,
            'no_identif': self.no_identif,
            'proveedor': self.proveedor,
            'sust_tp': self.sust_tp,
            'no_doc': self.no_doc,
            'fecha_emision': self.fecha_emision.strftime('%Y-%m-%d'),
            'valor_objeto_iva': float(self.valor_objeto_iva),
            'excento': float(self.excento),
            'base_0': float(self.base_0),
            'base_iva': float(self.base_iva),
            'monto_iva': float(self.monto_iva),
            'total': float(self.total),
            'no_retenc': self.no_retenc,
            'rt_iva': float(self.rt_iva),
            'rt_fte': float(self.rt_fte),
        }

    class Meta:
        db_table = 'tb_compraATS'
        verbose_name = "Compra ATS"
        verbose_name_plural = "Compras ATS"


class ATSVenta(models.Model):
    """Registro de ventas para ATS"""
    periodo = models.ForeignKey(ATSPeriodo, on_delete=models.CASCADE)
    tp_id = models.CharField(max_length=2, verbose_name="TP ID")
    no_identif = models.CharField(max_length=13, verbose_name="No. Identif.")
    cliente = models.CharField(max_length=200, verbose_name="Cliente")
    tp_comp = models.CharField(max_length=10, verbose_name="Tp.Comp.")
    no_docs = models.CharField(max_length=20, verbose_name="# Docs.")
    base_imp_0 = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Base Imp. 0%")
    base_imp_iva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Base Imp. IVA")
    monto_iva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto IVA")
    no_objeto_iva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="No Objeto IVA")
    ret_iva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Ret. IVA", default=0)
    ret_fte = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Ret. Fte.", default=0)

    def toJSON(self):
        return {
            'id': self.id,
            'tp_id': self.tp_id,
            'no_identif': self.no_identif,
            'cliente': self.cliente,
            'tp_comp': self.tp_comp,
            'no_docs': self.no_docs,
            'base_imp_0': float(self.base_imp_0),
            'base_imp_iva': float(self.base_imp_iva),
            'monto_iva': float(self.monto_iva),
            'no_objeto_iva': float(self.no_objeto_iva),
            'ret_iva': float(self.ret_iva),
            'ret_fte': float(self.ret_fte),
        }

    class Meta:
        db_table = 'tb_ventaATS'
        verbose_name = "Venta ATS"
        verbose_name_plural = "Ventas ATS"


class ATSAnulado(models.Model):
    """Registro de documentos anulados para ATS"""
    periodo = models.ForeignKey(ATSPeriodo, on_delete=models.CASCADE)
    tp_doc = models.CharField(max_length=2, verbose_name="Tp.Doc")
    fecha_emision = models.DateField(verbose_name="F.Emisión")
    no_documento = models.CharField(max_length=20, verbose_name="# Documento")
    id_emisor = models.CharField(max_length=13, verbose_name="ID. Emisor")
    razon_social_emisor = models.CharField(max_length=200, verbose_name="Razón Social Emisor")
    id_receptor = models.CharField(max_length=13, verbose_name="ID. Receptor")
    razon_social_receptor = models.CharField(max_length=200, verbose_name="Razón Social Receptor")
    clave_acceso = models.CharField(max_length=49, verbose_name="Clave Acceso")

    class Meta:
        db_table = 'tb_anuladoATS'
        verbose_name = "Anulado ATS"
        verbose_name_plural = "Anulados ATS"


class ATSImportacion(models.Model):
    """Registro de importaciones de archivos XML ATS"""
    archivo_xml = models.FileField(upload_to='ats_importaciones/')
    periodo_importado = models.CharField(max_length=20)
    informante = models.CharField(max_length=200)
    fecha_importacion = models.DateTimeField(auto_now_add=True)
    total_compras = models.IntegerField(default=0)
    total_ventas = models.IntegerField(default=0)
    total_anulados = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, default='importado')

    class Meta:
        db_table = 'tb_importacionATS'
        verbose_name = "Importación ATS"
        verbose_name_plural = "Importaciones ATS"
