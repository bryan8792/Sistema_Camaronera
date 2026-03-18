from django.db import connection
from app_user.models import Modulo, GrupoModulo


def user_has_perm(user, modulo_url, perm):

    # 🔥 No validar módulos en public
    if connection.schema_name == "public":
        return True

    if not user.is_authenticated:
        return False

    group = user.groups.first()
    if not group:
        return False

    modulo = Modulo.objects.filter(
        url=modulo_url,
        activo=True
    ).first()

    if not modulo:
        return False

    grupo_modulo = GrupoModulo.objects.filter(
        grupo=group,
        modulo=modulo
    ).first()

    if not grupo_modulo:
        return False

    return getattr(grupo_modulo, f'can_{perm}', False)
