from django.shortcuts import redirect
from app_user.models import Modulo, GrupoModulo

class ModulePermissionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path not in ['/login/', '/logout/']:
            path = request.path.strip('/')

            modulo = Modulo.objects.filter(url=path, activo=True).first()
            if modulo:
                grupo = request.user.groups.first()
                if not grupo:
                    return redirect('login')

                permiso = GrupoModulo.objects.filter(
                    grupo=grupo, modulo=modulo, can_view=True
                ).exists()

                if not permiso:
                    return redirect('/403/')
        return self.get_response(request)
