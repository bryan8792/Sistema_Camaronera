# Generated by Django 4.0.2 on 2025-06-29 00:59

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_venta', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CtasCollect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_joined', models.DateField(default=datetime.datetime.now)),
                ('end_date', models.DateField(default=datetime.datetime.now)),
                ('debt', models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                ('saldo', models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                ('state', models.BooleanField(default=True)),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_venta.sale')),
            ],
            options={
                'verbose_name': 'Cuenta por cobrar',
                'verbose_name_plural': 'Cuentas por cobrar',
                'db_table': 'tb_ctasCollect',
                'ordering': ['id'],
            },
        ),
    ]
