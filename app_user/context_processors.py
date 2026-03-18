from app_user.models import Modulo, GrupoModulo
from django.contrib.auth.models import Group


def menu_modulos(request):

    if not request.user.is_authenticated:
        return {'menu_modulos': []}

    grupos = request.user.groups.all()

    if not grupos.exists():
        return {'menu_modulos': []}

    permisos = GrupoModulo.objects.filter(
        grupo__in=grupos,
        can_view=True,
        modulo__activo=True
    ).select_related('modulo', 'modulo__tipo').order_by(
        'modulo__tipo__orden',
        'modulo__orden'
    )

    estructura = {}

    for permiso in permisos:
        tipo = permiso.modulo.tipo

        if tipo.id not in estructura:
            estructura[tipo.id] = {
                'tipo': tipo,
                'modulos': []
            }

        estructura[tipo.id]['modulos'].append(permiso.modulo)

    return {
        'menu_modulos': list(estructura.values())
    }