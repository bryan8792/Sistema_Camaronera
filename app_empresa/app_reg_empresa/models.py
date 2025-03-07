import base64
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
# Create your models here.

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

    def __str__(self):
        return self.numero

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     try:
    #         nueva_piscina = super(Piscinas, self).save()
    #
    #         if self.orden:
    #             self.numero = 'PISCINA %s' % self.orden
    #     except Exception as exc:
    #         pass

    def toJSON(self):
        item = model_to_dict(self)
        item['empresa'] = self.empresa.toJSON()
        return item

    class Meta:
        db_table = 'tb_piscina'
        verbose_name = 'Piscina'
        verbose_name_plural = 'Piscinas'
        ordering = ['id']