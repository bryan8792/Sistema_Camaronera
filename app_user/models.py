from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.forms import model_to_dict
from django.utils import timezone


# Modelo User personalizado (solo si lo necesitas)
class User(AbstractUser):
    imagen = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def toJSON(self):
        item = model_to_dict(self, exclude=['password'])
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['full_name'] = f"{self.first_name} {self.last_name}"
        return item


class TipoModulo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = "Tipo de Módulo"
        verbose_name_plural = "Tipos de Módulos"
        ordering = ['orden', 'nombre']


class Modulo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    url = models.CharField(max_length=200, verbose_name="URL")
    icono = models.CharField(max_length=50, default="fas fa-cog", verbose_name="Icono")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    tipo = models.ForeignKey(TipoModulo, on_delete=models.CASCADE, verbose_name="Tipo de Módulo")
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    def toJSON(self):
        item = model_to_dict(self)
        item['tipo'] = self.tipo.nombre if self.tipo else ''
        return item

    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        ordering = ['tipo__orden', 'orden', 'nombre']


class GrupoModulo(models.Model):
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('grupo', 'modulo')
        verbose_name = "Grupo-Módulo"
        verbose_name_plural = "Grupos-Módulos"

    def __str__(self):
        return f"{self.grupo.name} - {self.modulo.nombre}"