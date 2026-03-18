from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.db import connection
from app_empresa.app_reg_empresa.models import Empresa


class loginFormView(LoginView):
    template_name = 'app_template/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tenant = getattr(connection, 'tenant', None)
        empresa = None

        if tenant and tenant.schema_name != 'public':
            empresa = Empresa.objects.filter(schema_name=tenant.schema_name).first()

        if empresa:
            context['nombre'] = empresa.nombre
            context['empresa'] = empresa
            context['logo'] = empresa.logo.url if hasattr(empresa, 'logo') and empresa.logo else None
        else:
            context['nombre'] = 'Sistema'

        return context
