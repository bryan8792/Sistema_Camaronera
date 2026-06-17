from django.db import models
from app_empresa.app_reg_empresa.models import Piscinas
from app_user.models import User
from django.db.models import Sum, Avg
# Create your models here.


# CABECERA
class TransferenciaLarva(models.Model):
    fecha_larva_sembrada = models.DateField()
    cantidad_larva_sembrada = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    fecha_siembra_piscina = models.DateField()
    laboratorio = models.CharField(max_length=100, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Transferencia #{self.id}"

    # TOTAL TRANSFERIDO
    @property
    def total_transferido_general(self):
        total = self.detalles.aggregate(total=Sum('total_transferido'))
        return total['total'] or 0

    # TOTAL ANIMALES SEMBRADOS
    @property
    def total_animales_sembrados(self):
        total = self.detalles.aggregate(total=Sum('animales_sembrados'))
        return total['total'] or 0

    # TOTAL HECTAREAS
    @property
    def total_hectareas(self):
        total = self.detalles.aggregate(total=Sum('hectareas'))
        return total['total'] or 0

    # PROMEDIO SUPERVIVENCIA
    @property
    def promedio_supervivencia(self):
        promedio = self.detalles.aggregate(promedio=Avg('porcentaje_sobrevivencia'))
        return round(promedio['promedio'] or 0, 2)

    # CANTIDAD DE PISCINAS
    @property
    def cantidad_piscinas(self):
        return self.detalles.count()

    class Meta:
        db_table = 'transferencia_larva'
        verbose_name = 'Transferencia Larva'
        verbose_name_plural = 'Transferencias Larvas'
        ordering = ['-id']


# DETALLE
class DetalleTransferenciaLarva(models.Model):
    transferencia = models.ForeignKey(TransferenciaLarva, on_delete=models.CASCADE, related_name='detalles')
    desde_piscina = models.CharField(max_length=50)
    maduracion = models.CharField(max_length=100)
    hacia_piscina = models.ForeignKey(Piscinas, on_delete=models.CASCADE)
    sector = models.CharField(max_length=50)
    hectareas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    animales_sembrados = models.DecimalField(max_digits=20, decimal_places=0, default=0)
    peso_siembra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    animales_ha = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    edad = models.IntegerField(default=0)
    total_transferido = models.DecimalField(max_digits=20, decimal_places=0, default=0)
    porcentaje_sobrevivencia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    aguaje = models.CharField(max_length=50, blank=True, null=True)
    numero_guia = models.CharField(max_length=100, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return (
            f"{self.desde_piscina} -> "
            f"{self.hacia_piscina}"
        )

    class Meta:
        db_table = 'detalle_transferencia_larva'
        verbose_name = 'Detalle Transferencia'
        verbose_name_plural = 'Detalles Transferencia'
        ordering = ['id']