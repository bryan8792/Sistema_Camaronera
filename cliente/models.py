from django.db import models
from django.forms import model_to_dict
from datetime import datetime
from app_user.models import User
from utilities.choices import *

# Create your models here.
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=13, unique=True, verbose_name='Número de cedula o ruc')
    movil = models.CharField(max_length=10, unique=True, verbose_name='Teléfono')
    nacimiento = models.DateField(default=datetime.now, verbose_name='Fecha de nacimiento')
    direccion = models.CharField(max_length=500, verbose_name='Dirección')
    identification_type = models.CharField(max_length=30, choices=IDENTIFICATION_TYPE, default=IDENTIFICATION_TYPE[0][0], verbose_name='Tipo de identificación')
    send_email_invoice = models.BooleanField(default=True, verbose_name='¿Enviar email de factura?')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.usuario.first_name} ({self.usuario.last_name})'

    def birthdate_format(self):
        return self.nacimiento.strftime('%Y-%m-%d')

    def toJSON(self):
        item = model_to_dict(self)
        item['text'] = self.get_full_name()
        item['usuario'] = self.usuario.toJSON()
        item['identification_type'] = {'id': self.identification_type, 'name': self.get_identification_type_display()}
        item['nacimiento'] = self.nacimiento.strftime('%Y-%m-%d')
        return item

    def delete(self, using=None, keep_parents=False):
        super(Cliente, self).delete()
        try:
            self.usuario.delete()
        except:
            pass

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'