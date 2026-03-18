from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import *
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from Sistema_Camaronera import settings
from app_empresa.app_reg_empresa.forms import EmpresaForm
from app_empresa.app_reg_empresa.models import Empresa, Domain, PeriodoFiscal
from django.contrib import messages
from django.db import transaction
from django_tenants.utils import schema_context
# from app_empresa.app_reg_empresa.services import clonar_empresa_en_tenant
from app_empresa.app_reg_empresa.utils import clonar_empresa_en_tenant
from app_empresa.app_reg_empresa.utils import clonar_datos_base_en_tenant
from django.db import connection
import unicodedata
from django.http import HttpResponseForbidden


# Vista basada en funcion
def listarEmpresa(request):
    data = {
        'nombre': 'Empresa',
        'empresa': Empresa.objects.all()
    }
    return render(request, 'app_empresa/empresa_listar.html', data)



class crearEmpresaView(CreateView):
    model = Empresa
    form_class = EmpresaForm
    success_url = reverse_lazy('app_empresa:listar_empresa')

    def get_template_names(self):
        if self.request.tenant.schema_name == 'public':
            return ['app_empresa/empresa_crear_public.html']
        return ['app_empresa/empresa_crear_tenant.html']

    def dispatch(self, request, *args, **kwargs):
        # 🔥 LIMPIAR MENSAJES VIEJOS DE SESION
        storage = messages.get_messages(request)
        for _ in storage:
            pass
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        with transaction.atomic():
            self.object = form.save(commit=False)

            # generar schema_name automáticamente
            nombre = self.object.nombre.lower()
            nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
            nombre = nombre.replace(" ", "")

            self.object.schema_name = nombre

            self.object.save()

        messages.success(
            self.request,
            f'Empresa "{self.object.nombre}" creada correctamente. '
            f'Ahora debe crear un Periodo Fiscal.'
        )

        return redirect(self.success_url)

    def form_invalid(self, form):
        print(form.errors)  # 👈 MOSTRAR ERROR EN CONSOLA
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class actualizarEmpresaView(UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'app_empresa/empresa_crear.html'
    success_url = reverse_lazy('app_empresa:listar_empresa')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Empresa'
        return context


class eliminarEmpresaView(DeleteView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'app_empresa/empresa_eliminar.html'
    success_url = reverse_lazy('app_empresa:listar_empresa')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Empresa'
        return context


class listarEmpresaView(ListView):
    context_object_name = 'object_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # 🔹 AQUI DECIDIMOS QUE TEMPLATE USAR
    def get_template_names(self):
        if self.request.tenant.schema_name == 'public':
            return ['app_empresa/empresa_listar_public.html']
        return ['app_empresa/empresa_listar_tenant.html']

    def get_queryset(self):
        tenant = self.request.tenant

        # PUBLIC → todas las empresas (desde public)
        if tenant.schema_name == 'public':
            with schema_context('public'):
                return Empresa.objects.all()

        # TENANT → solo la empresa
        # return Empresa.objects.filter(scheme=tenant)
        return Empresa.objects.all()


class listarDashboardBIO(TemplateView):
    template_name = 'app_template/dashboard_bio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with schema_context('public'):
            empresas = Empresa.objects.all()
            periodos = PeriodoFiscal.objects.all()

        context['empresas'] = empresas
        context['periodos'] = periodos

        return context


class empresaTenantView(UpdateView):
    model = Empresa
    template_name = 'app_empresa/empresa_tenant.html'
    form_class = EmpresaForm

    def get_object(self):
        return self.request.tenant.empresa



class TenantDashboardView(TemplateView):
    template_name = 'dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        # si entra por public no debe ver dashboard
        if request.tenant.schema_name == 'public':
            from django.shortcuts import redirect
            return redirect('app_empresa:listar_empresa')
        return super().dispatch(request, *args, **kwargs)




class PeriodoFiscalListView(ListView):
    model = PeriodoFiscal
    template_name = "app_periodos/periodo_list.html"
    context_object_name = "periodos"

    def dispatch(self, request, *args, **kwargs):

        # solo desde schema public
        if connection.schema_name != 'public':
            return HttpResponseForbidden("Solo disponible desde public")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        from django_tenants.utils import schema_context

        with schema_context('public'):
            return PeriodoFiscal.objects.all()


class PeriodoFiscalCreateView(CreateView):

    model = PeriodoFiscal
    fields = ['empresa', 'anio']
    template_name = "app_periodos/periodo_form.html"
    success_url = reverse_lazy('app_empresa:periodo_list')

    def dispatch(self, request, *args, **kwargs):

        if request.tenant.schema_name != 'public':
            return redirect('app_empresa:listar_empresa')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        with schema_context('public'):
            form.save()

        messages.success(
            self.request,
            "Periodo fiscal creado correctamente. El tenant fue generado automáticamente."
        )

        return redirect(self.success_url)

    def form_invalid(self, form):

        messages.error(
            self.request,
            "Error al crear el periodo fiscal."
        )

        return super().form_invalid(form)


class PeriodoFiscalUpdateView(UpdateView):

    model = PeriodoFiscal
    fields = ['anio', 'activo', 'cerrado']
    template_name = 'app_periodos/periodo_form.html'
    success_url = reverse_lazy('app_empresa:periodo_list')

    def form_valid(self, form):

        messages.success(
            self.request,
            "Periodo fiscal actualizado correctamente."
        )

        return super().form_valid(form)


class PeriodoFiscalDeleteView(DeleteView):

    model = PeriodoFiscal
    template_name = 'app_periodos/periodo_delete.html'
    success_url = reverse_lazy('app_empresa:periodo_list')

    def delete(self, request, *args, **kwargs):

        messages.success(
            request,
            "Periodo fiscal eliminado correctamente."
        )

        return super().delete(request, *args, **kwargs)




