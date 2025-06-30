from datetime import datetime
from django.db import models
from django.forms import model_to_dict
from app_user.models import User
from utilities.choices import *


# Create your models here.
class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dni = models.CharField(max_length=13, unique=True, verbose_name='Número de cedula o ruc')
    mobile = models.CharField(max_length=10, unique=True, verbose_name='Teléfono')
    birthdate = models.DateField(default=datetime.now, verbose_name='Fecha de nacimiento')
    address = models.CharField(max_length=500, verbose_name='Dirección')
    identification_type = models.CharField(max_length=30, choices=IDENTIFICATION_TYPE, default=IDENTIFICATION_TYPE[0][0], verbose_name='Tipo de identificación')
    send_email_invoice = models.BooleanField(default=True, verbose_name='¿Enviar email de factura?')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.user.names} ({self.dni})'

    def birthdate_format(self):
        return self.birthdate.strftime('%Y-%m-%d')

    def toJSON(self):
        item = model_to_dict(self)
        item['text'] = self.get_full_name()
        item['user'] = self.user.toJSON()
        item['identification_type'] = {'id': self.identification_type, 'name': self.get_identification_type_display()}
        item['birthdate'] = self.birthdate.strftime('%Y-%m-%d')
        return item

    def delete(self, using=None, keep_parents=False):
        super(Client, self).delete()
        try:
            self.user.delete()
        except:
            pass

    class Meta:
        db_table = 'tb_cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['id']