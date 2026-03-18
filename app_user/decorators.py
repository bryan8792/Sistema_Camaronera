from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from app_user.services.permissions import user_has_perm

def permission_required(modulo_url, perm):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not user_has_perm(request.user, modulo_url, perm):
                return HttpResponseForbidden("No tiene permiso.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
