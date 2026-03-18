import base64
import math
import tempfile
import time
import unicodedata
from io import BytesIO
from xml.etree import ElementTree
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import models
from datetime import datetime
from django.forms import model_to_dict
from Sistema_Camaronera.settings import MEDIA_URL, STATIC_URL, BASE_DIR
from app_empresa.app_reg_empresa.utils import *
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
from app_tenant.models import Scheme, Domain
from django.db import models
from django.conf import settings
from django_tenants.utils import schema_context
from django.db import transaction


class Empresa(models.Model):
    scheme = models.OneToOneField('app_tenant.Scheme', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Esquema', related_name='empresa')
    schema_name = models.CharField(max_length=30, null=True, blank=True, unique=True, verbose_name='Nombre del esquema', help_text='Ej: localpasaje (sera el subdominio: localpasaje.tudominio.com)')
    ruc = models.CharField(max_length=13, verbose_name='Numero de RUC', null=True, blank=True)
    nombre = models.CharField(max_length=150, verbose_name='Nombre Empresa')
    business_name = models.CharField(max_length=50, verbose_name='Razón social', null=True, blank=True)
    tradename = models.CharField(max_length=50, verbose_name='Nombre Comercial', null=True, blank=True)
    direccion = models.CharField(max_length=150, verbose_name='Direccion ', null=True, blank=True)
    main_address = models.CharField(max_length=200, verbose_name='Dirección del Establecimiento Matriz', null=True, blank=True)
    establishment_address = models.CharField(max_length=200, verbose_name='Dirección del Establecimiento Emisor', null=True, blank=True)
    siglas = models.CharField(max_length=150, verbose_name='Siglas ')
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

    # def create_schema(self):
    #     """Crea el esquema en PostgreSQL y el dominio asociado"""
    #
    #     if not self.schema_name:
    #         return None
    #
    #     # Verificar si ya existe el esquema
    #     if Scheme.objects.filter(schema_name=self.schema_name).exists():
    #         return Scheme.objects.get(schema_name=self.schema_name)
    #
    #     # Crear el esquema
    #     scheme = Scheme.objects.create(
    #         name=self.nombre or self.schema_name,
    #         schema_name=self.schema_name
    #     )
    #
    #     # Crear el dominio (subdominio)
    #     Domain.objects.create(
    #         domain=f'{self.schema_name}.{settings.DOMAIN}',
    #         tenant=scheme,
    #         is_primary=True
    #     )
    #
    #     return scheme

    # def save(self, *args, **kwargs):
    #     # Si es nuevo, tiene schema_name y no tiene scheme asignado
    #     if self.schema_name and not self.scheme:
    #         self.scheme = self.create_schema()
    #     super().save(*args, **kwargs)

    def get_tenant_url(self):
        """Retorna la URL del tenant"""
        if self.schema_name:
            return f'http://{self.schema_name}.{settings.DOMAIN}/'
        return None

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
        item['tenant_url'] = self.get_tenant_url()
        item['schema_name'] = self.schema_name
        return item

    class Meta:
        db_table = 'tb_empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['id']


class PeriodoFiscal(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='periodos',  verbose_name='Empresa')
    anio = models.IntegerField(verbose_name='Año')
    schema_name = models.CharField(max_length=30, unique=True, verbose_name='Nombre del schema')
    scheme = models.OneToOneField('app_tenant.Scheme', on_delete=models.CASCADE, null=True, blank=True)
    auto_create_schema = True
    activo = models.BooleanField(default=True)
    cerrado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.empresa.nombre} - {self.anio}"

    # 🔥 AQUÍ VA create_schema
    def create_schema(self):
        if Scheme.objects.filter(schema_name=self.schema_name).exists():
            return Scheme.objects.get(schema_name=self.schema_name)

        scheme = Scheme.objects.create(
            name=f"{self.empresa.nombre} {self.anio}",
            schema_name=self.schema_name
        )

        Domain.objects.create(
            domain=f'{self.schema_name}.{settings.DOMAIN}',
            # domain=f'{self.schema_name}.lvh.me',
            tenant=scheme,
            is_primary=True
        )

        return scheme

    # 🔥 AQUÍ VA save
    # def save(self, *args, **kwargs):
    #
    #     creando = self.pk is None
    #
    #     if self.schema_name and not self.scheme:
    #         self.scheme = self.create_schema()
    #
    #     super().save(*args, **kwargs)
    #
    #     # 🔥 SOLO si es nuevo periodo
    #     if creando:
    #
    #         # 1️⃣ Clonar empresa dentro del nuevo schema
    #         with schema_context(self.schema_name):
    #
    #             if not Empresa.objects.exists():
    #                 Empresa.objects.create(
    #                     nombre=self.empresa.nombre,
    #                     ruc=self.empresa.ruc,
    #                     business_name=self.empresa.business_name,
    #                     tradename=self.empresa.tradename,
    #                     direccion=self.empresa.direccion,
    #                     siglas=self.empresa.siglas,
    #                     iva=self.empresa.iva,
    #                     vat_percentage=self.empresa.vat_percentage,
    #                     obligated_accounting=self.empresa.obligated_accounting,
    #                     environment_type=self.empresa.environment_type,
    #                     emission_type=self.empresa.emission_type,
    #                     retention_agent=self.empresa.retention_agent,
    #                     mobile=self.empresa.mobile,
    #                     phone=self.empresa.phone,
    #                     email=self.empresa.email,
    #                     website=self.empresa.website,
    #                     description=self.empresa.description,
    #                 )

    def save(self, *args, **kwargs):

        creando = self.pk is None

        # Generar schema automáticamente
        if not self.schema_name:

            empresa_slug = (
                self.empresa.nombre
                .lower()
                .replace(" ", "")
                .replace(".", "")
            )

            self.schema_name = f"{empresa_slug}{self.anio}"

        # Crear tenant
        if not self.scheme:
            self.scheme = self.create_schema()

        super().save(*args, **kwargs)

        # Solo cuando es nuevo
        if creando:

            # Migrar tablas en el schema
            call_command(
                "migrate_schemas",
                schema_name=self.schema_name,
                interactive=False
            )

            # 1️⃣ crear empresa dentro del tenant
            clonar_empresa_en_tenant(self.empresa, self.schema_name)

            # 2️⃣ clonar configuración base
            clonar_datos_base_en_tenant(self.schema_name)

            # Clonar empresa dentro del tenant
            with schema_context(self.schema_name):

                if not Empresa.objects.exists():
                    Empresa.objects.create(
                        nombre=self.empresa.nombre,
                        ruc=self.empresa.ruc
                    )

        User = get_user_model()

        with schema_context(self.schema_name):

            if not User.objects.filter(username="bryan").exists():
                User.objects.create_superuser(
                    username="bryan",
                    password="bryan",
                    email="bxbr92@hotmial.com"
                )

    def toJSON(self):
        item = model_to_dict(self)
        item['empresa'] = self.empresa.toJSON()
        return item

    class Meta:
        db_table = 'tb_periodo_fiscal'
        verbose_name = 'Periodo Fiscal'
        verbose_name_plural = 'Periodos Fiscales'
        unique_together = ('empresa', 'anio')

