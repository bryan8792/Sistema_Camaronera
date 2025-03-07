
from django.db import models
from datetime import datetime


# Create your models here.
class Tipo_Empleado(models.Model):
    tipo = models.CharField(max_length=150, verbose_name='Tipo')
    descripcion = models.CharField(max_length=400, verbose_name='Descripcion')

    def __str__(self):
        return self.tipo

    class Meta:
        db_table = 'tipo_empleado'
        verbose_name = 'Tipo'
        verbose_name_plural = 'Tipos'
        ordering = ['id']


class Empleado(models.Model):
    tipo = models.ForeignKey(Tipo_Empleado, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=150, verbose_name='Nombres')
    apellidos = models.CharField(max_length=150, verbose_name='Apellidos')
    cedula = models.CharField(max_length=10, unique=True, verbose_name='Cedula')
    fecha_registro = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    fecha_creacion = models.DateTimeField(auto_now=True)
    fecha_actualizacion = models.DateTimeField(auto_now_add=True)
    edad = models.PositiveIntegerField(default=0)
    salario = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    estado = models.BooleanField(default=True)
    # genero = models.CharField(max_length=50)
    foto = models.ImageField(upload_to='img_user/%Y/%m/%d', null=True, blank=True)
    cvitae = models.FileField(upload_to='cvitae/%Y/%m/%d', null=True, blank=True)

    def __str__(self):
        return self.nombres

    class Meta:
        db_table = 'empleado'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['id']