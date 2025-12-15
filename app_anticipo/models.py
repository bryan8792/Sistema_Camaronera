from django.db import models
from django.forms import model_to_dict
from app_empresa.app_reg_empresa.models import Empresa
from app_contabilidad_planCuentas.models import PlanCuenta


class TipoPago(models.Model):
    """
    Tipos de pago: CONTADO, CREDITO, etc.
    Los puede crear el usuario dinámicamente
    """
    nombre = models.CharField(max_length=50, verbose_name='Tipo de Pago', unique=True)
    descripcion = models.CharField(max_length=200, verbose_name='Descripción', null=True, blank=True)
    estado = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.nombre

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        db_table = 'tb_tipo_pago'
        verbose_name = 'Tipo de Pago'
        verbose_name_plural = 'Tipos de Pago'
        ordering = ['nombre']


class FormaPagoOpcion(models.Model):
    """
    Formas de pago disponibles: EFECTIVO, CHEQUE, TRANSFERENCIA, etc.
    Los puede crear el usuario dinámicamente
    """
    nombre = models.CharField(max_length=100, verbose_name='Forma de Pago', unique=True)
    descripcion = models.CharField(max_length=200, verbose_name='Descripción', null=True, blank=True)
    estado = models.BooleanField(default=True, verbose_name='Estado')
    codigo = models.CharField(max_length=20, verbose_name='Código', null=True, blank=True,
                              help_text='Código para identificación rápida')

    def __str__(self):
        return self.nombre

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        db_table = 'tb_forma_pago_opcion'
        verbose_name = 'Forma de Pago'
        verbose_name_plural = 'Formas de Pago'
        ordering = ['nombre']


class Anticipo(models.Model):
    """
    Registro de anticipos a clientes
    """
    TIPO_CAJA_CHOICES = [
        ('PRINCIPAL', 'Principal'),
        ('SECUNDARIA', 'Secundaria'),
    ]

    TIPO_CLIENTE_CHOICES = [
        ('CLIENTE', 'Cliente'),
        ('PROVEEDOR', 'Proveedor'),
    ]

    TIPO_IDENT_CHOICES = [
        ('CEDULA', 'Cédula'),
        ('RUC', 'RUC'),
        ('PASAPORTE', 'Pasaporte'),
    ]

    # Información de caja y cliente
    caja = models.CharField(max_length=50, choices=TIPO_CAJA_CHOICES, default='PRINCIPAL', verbose_name='Caja')
    tipo_cliente = models.CharField(max_length=50, choices=TIPO_CLIENTE_CHOICES, default='CLIENTE', verbose_name='Tipo')

    # Centro de costo es la empresa que da el anticipo (BIO, PSM)
    centro_costo = models.ForeignKey(Empresa, on_delete=models.PROTECT, verbose_name='Centro de Costo (Empresa)',
                                     related_name='anticipos_otorgados')

    # Información del cliente que recibe el anticipo
    tipo_identificacion = models.CharField(max_length=50, choices=TIPO_IDENT_CHOICES, default='CEDULA',
                                           verbose_name='Tipo Identificación')
    identificacion = models.CharField(max_length=20, verbose_name='Identificación')
    razon_social = models.CharField(max_length=200, verbose_name='Razón Social')
    nombre_comercial = models.CharField(max_length=200, verbose_name='Nombre Comercial', null=True, blank=True)
    telefono = models.CharField(max_length=15, verbose_name='Teléfono', null=True, blank=True)
    celular = models.CharField(max_length=15, verbose_name='Celular', null=True, blank=True)
    email = models.EmailField(verbose_name='Email', null=True, blank=True)
    ciudad = models.CharField(max_length=100, verbose_name='Ciudad', null=True, blank=True)
    direccion = models.TextField(verbose_name='Dirección', null=True, blank=True)

    # Información del anticipo
    fecha = models.DateField(verbose_name='Fecha')
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto', default=0.00)
    concepto = models.TextField(verbose_name='Concepto')

    # Categoría contable de referencia según la empresa
    categoria_contable = models.ForeignKey(PlanCuenta, on_delete=models.PROTECT, verbose_name='Categoría Contable',
                                           null=True, blank=True)

    # Metadata
    estado = models.BooleanField(default=True, verbose_name='Estado')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha Actualización')

    def __str__(self):
        return f"Anticipo {self.id} - {self.razon_social} - ${self.monto}"

    def toJSON(self):
        item = model_to_dict(self)
        item['centro_costo'] = self.centro_costo.toJSON() if self.centro_costo else None
        item['categoria_contable'] = self.categoria_contable.toJSON() if self.categoria_contable else None
        if self.fecha:
            if isinstance(self.fecha, str):
                item['fecha'] = self.fecha  # Ya es string
            else:
                item['fecha'] = self.fecha.strftime('%Y-%m-%d')  # Convertir datetime a string
        else:
            item['fecha'] = None
        item['monto'] = float(self.monto)
        item['formas_pago'] = [fp.toJSON() for fp in self.formas_pago.all()]
        return item

    class Meta:
        db_table = 'tb_anticipo'
        verbose_name = 'Anticipo'
        verbose_name_plural = 'Anticipos'
        ordering = ['-fecha', '-id']


class FormaPago(models.Model):
    """
    Detalle de las formas de pago de un anticipo
    Permite múltiples formas de pago para un mismo anticipo
    """
    anticipo = models.ForeignKey(Anticipo, on_delete=models.CASCADE, related_name='formas_pago',
                                 verbose_name='Anticipo')
    tipo = models.ForeignKey(TipoPago, on_delete=models.PROTECT, verbose_name='Tipo')
    forma = models.ForeignKey(FormaPagoOpcion, on_delete=models.PROTECT, verbose_name='Forma')
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor', default=0.00)

    # Campos adicionales según la forma de pago
    referencia = models.CharField(max_length=100, verbose_name='Referencia', null=True, blank=True,
                                  help_text='Número de cheque, transferencia, etc.')
    banco = models.CharField(max_length=100, verbose_name='Banco', null=True, blank=True)
    observacion = models.TextField(verbose_name='Observación', null=True, blank=True)

    def __str__(self):
        return f"{self.forma} - ${self.valor}"

    def toJSON(self):
        item = model_to_dict(self)
        item['anticipo_id'] = self.anticipo.id
        item['tipo'] = self.tipo.toJSON() if self.tipo else None
        item['forma'] = self.forma.toJSON() if self.forma else None
        item['valor'] = float(self.valor)
        return item

    class Meta:
        db_table = 'tb_forma_pago'
        verbose_name = 'Forma de Pago'
        verbose_name_plural = 'Formas de Pago'
        ordering = ['id']
