from django_tenants.utils import schema_context
from .models import Empresa

def clonar_empresa_en_tenant(instance):
    with schema_context(instance.schema_name):

        # Evitar duplicados
        if Empresa.objects.exists():
            return

        Empresa.objects.create(
            nombre=instance.nombre,
            ruc=instance.ruc,
            schema_name=instance.schema_name,
            estado=instance.estado,
            business_name=instance.business_name,
            tradename=instance.tradename,
            siglas=instance.siglas,
            iva=instance.iva,
            vat_percentage=instance.vat_percentage,
        )
