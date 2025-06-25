from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.forms import model_to_dict
from Sistema_Camaronera.settings import MEDIA_URL, STATIC_URL


class User(AbstractUser):
    imagen = models.ImageField(upload_to='imag_user/%Y/%m/%d', null=True, blank=True)

    def get_image(self):
        if self.imagen:
            return '{}{}'.format(MEDIA_URL, self.imagen)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    def toJSON(self):
        item = model_to_dict(self, exclude=['last_login', 'email_reset_token', 'password', 'user_permissions'])
        item['imagen'] = self.get_image()
        item['full_name'] = self.get_full_name()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['last_login'] = None if self.last_login is None else self.last_login.strftime('%Y-%m-%d')
        item['groups'] = [{'id': g.id, 'name': g.name} for g in self.groups.all()]
        item['permissions'] = [{'id': p.id, 'name': p.name} for p in self.user_permissions.all()]
        return item

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.set_password(self.password)
        else:
            user = User.objects.get(pk=self.pk)
            if user.password != self.password:
                self.set_password(self.password)
        super().save(*args, **kwargs)


class TipoModulo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Tipo de Módulo'
        verbose_name_plural = 'Tipos de Módulos'


class Modulo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=200, blank=True, null=True)
    icono = models.CharField(max_length=50, default='fas fa-cog')
    tipo = models.ForeignKey(TipoModulo, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    def toJSON(self):
        item = model_to_dict(self)
        item['tipo'] = self.tipo.nombre if self.tipo else ''
        return item

    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['orden', 'nombre']


class GrupoModulo(models.Model):
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.grupo.name} - {self.modulo.nombre}"

    class Meta:
        unique_together = ('grupo', 'modulo')
        verbose_name = 'Grupo Módulo'
        verbose_name_plural = 'Grupos Módulos'