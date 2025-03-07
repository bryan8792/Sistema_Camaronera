from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import model_to_dict
from Sistema_Camaronera.settings import MEDIA_URL, STATIC_URL


# Create your models here.
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
        return item

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.set_password(self.password)
        else:
            user = User.objects.get(pk=self.pk)
            if user.password != self.password:
                self.set_password(self.password)
        super().save(*args, **kwargs)
