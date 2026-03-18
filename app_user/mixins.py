from django.shortcuts import redirect
from app_user.models import GrupoModulo

class ModuloRequiredMixin:
    modulo = None
    permiso = 'view'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        grupos = request.user.groups.all()

        if not GrupoModulo.objects.filter(
            grupo__in=grupos,
            modulo__nombre=self.modulo,
            **{f'can_{self.permiso}': True}
        ).exists():
            return redirect('/')

        return super().dispatch(request, *args, **kwargs)
