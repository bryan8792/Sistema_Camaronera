from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.forms import model_to_dict
from django.utils import timezone
import uuid
from Sistema_Camaronera import settings
from crum import get_current_request
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone


class User(AbstractUser):
    names = models.CharField(max_length=150, null=True, blank=True, verbose_name='Nombres')
    username = models.CharField(max_length=150, unique=True, verbose_name='Username')
    imagen = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(null=True, blank=True, verbose_name='Correo electrónico')
    is_active = models.BooleanField(default=True, verbose_name='Estado')
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_change_password = models.BooleanField(default=False)
    email_reset_token = models.TextField(null=True, blank=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def toJSON(self):
        item = model_to_dict(self, exclude=['last_login', 'email_reset_token', 'password', 'user_permissions'])
        item['imagen'] = self.get_image()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['groups'] = [{'id': i.id, 'name': i.name} for i in self.groups.all()]
        item['last_login'] = None if self.last_login is None else self.last_login.strftime('%Y-%m-%d')
        return item

    def get_full_name(self):
        return self.names

    def generate_token_email(self):
        return str(uuid.uuid4())

    def get_image(self):
        if self.imagen:
            return f'{settings.MEDIA_URL}{self.imagen}'
        return f'{settings.STATIC_URL}img/default/empty.png'

    def get_group_id_session(self):
        try:
            request = get_current_request()
            return int(request.session['group'].id)
        except:
            return 0

    def set_group_session(self):
        try:
            request = get_current_request()
            groups = request.user.groups.all()
            if groups:
                if 'group' not in request.session:
                    request.session['group'] = groups[0]
        except:
            pass

    def create_or_update_password(self, password):
        if self.pk is None:
            self.set_password(password)
        else:
            user = User.objects.get(pk=self.pk)
            if user.password != password:
                self.set_password(password)

    def get_short_name(self):
        if self.names is not None:
            names = self.names.split(' ')
            if len(names) > 1:
                return f'{names[0]} {names[1]}'
        return self.names

    def has_at_least_one_group(self):
        return self.groups.all().count() > 0

    def has_more_than_one_group(self):
        return self.groups.all().count() > 1

    def is_client(self):
        return hasattr(self, 'client')

    def __str__(self):
        return self.names

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


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