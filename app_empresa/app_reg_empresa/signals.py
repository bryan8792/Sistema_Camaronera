from django.db.models.signals import post_save
from django.dispatch import receiver
from django_tenants.utils import schema_context

from app_user.services.sync_service import sync_tenant_modulos
from .models import Empresa


@receiver(post_save, sender=Empresa)
def clonar_empresa_en_tenant(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.schema_name:
        return

    schema = instance.schema_name

    with schema_context(schema):

        # Evitar duplicados
        if Empresa.objects.exists():
            return

        Empresa.objects.create(
            scheme=None,
            schema_name=schema,
            ruc=instance.ruc,
            nombre=instance.nombre,
            business_name=instance.business_name,
            tradename=instance.tradename,
            direccion=instance.direccion,
            main_address=instance.main_address,
            establishment_address=instance.establishment_address,
            siglas=instance.siglas,
            establishment_code=instance.establishment_code,
            issuing_point_code=instance.issuing_point_code,
            special_taxpayer=instance.special_taxpayer,
            aperturada=instance.aperturada,
            actividad=instance.actividad,
            estado=instance.estado,
            logo=instance.logo,
            obligated_accounting=instance.obligated_accounting,
            environment_type=instance.environment_type,
            emission_type=instance.emission_type,
            retention_agent=instance.retention_agent,
            mobile=instance.mobile,
            phone=instance.phone,
            email=instance.email,
            website=instance.website,
            description=instance.description,
            iva=instance.iva,
            vat_percentage=instance.vat_percentage,
        )

    sync_tenant_modulos(schema)

    print(f"Empresa y módulos creados para schema {schema}")
