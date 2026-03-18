
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from app_empresa.app_reg_empresa.models import Empresa
from django.views.generic import TemplateView
from django.shortcuts import redirect


class IndexView(TemplateView):

    def get(self, request, *args, **kwargs):

        # SI ES PUBLIC → panel SaaS
        if request.tenant.schema_name == 'public':
            return self.render_to_response(self.get_context_data())

        # SI ES TENANT → redirigir al dashboard
        return redirect('tenant_dashboard')


    def get_template_names(self):
        return ['base_public.html']


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'PSM & BIO Sistema Informático'
        context['nombres'] = 'PSM & BIO Sistema Informático'
        context['empresas'] = Empresa.objects.filter(estado=True)
        return context


# class IndexView(TemplateView):
#     template_name = "app_template/index.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'PSM & BIO Sistema Informático'
#         context['empresas'] = Empresa.objects.filter(estado=True)
#
#         return context


