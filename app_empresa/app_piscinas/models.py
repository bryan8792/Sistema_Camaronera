from django.db import models
from django.core.files.base import ContentFile
from django.db.models import FloatField
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.forms import model_to_dict
from django.utils import timezone
from django.core.exceptions import ValidationError
from app_empresa.app_reg_empresa.models import Empresa


# Create your models here.
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


