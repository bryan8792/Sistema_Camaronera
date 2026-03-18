from django_tenants.utils import get_tenant

from Sistema_Camaronera import settings
from app_empresa.app_reg_empresa.models import Empresa


def empresa_actual(request):
    tenant = get_tenant(request)

    if tenant.schema_name == 'public':
        return {'empresa_actual': None}

    try:
        return {'empresa_actual': Empresa.objects.first()}
    except:
        return {'empresa_actual': None}

