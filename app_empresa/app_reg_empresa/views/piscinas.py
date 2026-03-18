
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from app_empresa.app_piscinas.forms import PiscinasForm
from app_empresa.app_piscinas.models import Piscinas, PiscinaHistorial
from app_empresa.app_reg_empresa.forms import EmpresaForm
from app_empresa.app_reg_empresa.models import Empresa
from django.shortcuts import get_object_or_404
from datetime import datetime
from collections import OrderedDict
from django.contrib import messages


# Piscinas de las Empresas - aqio las listo abajo por clases hago lo mismo y es mejor abajo
def listarPiscina(request):
    data = {
        'nombre': 'Piscinas',
        'piscinas': Piscinas.objects.all(),
        'empresa': Empresa.objects.all()
    }
    return render(request, 'app_empresa/app_piscinas/piscinas_listar.html', data)


class reportePiscinasView(TemplateView):
    template_name = 'app_empresa/app_piscinas/piscinas_reporte.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener parámetros de filtro
        fecha_desde = self.request.GET.get('fecha_desde', '')
        fecha_hasta = self.request.GET.get('fecha_hasta', '')
        empresa_id = self.request.GET.get('empresa', '')

        # Query base de piscinas
        piscinas = Piscinas.objects.all().select_related('empresa', 'plan_cuenta', 'cuenta_suministros')

        # Aplicar filtros si existen
        if empresa_id:
            piscinas = piscinas.filter(empresa_id=empresa_id)
            try:
                empresa_obj = Empresa.objects.get(id=empresa_id)
                context['empresa_nombre'] = empresa_obj.nombre
            except Empresa.DoesNotExist:
                context['empresa_nombre'] = None
        else:
            context['empresa_nombre'] = None

        # Filtrar por fechas si el modelo tiene campo de fecha (ajusta según tu modelo)
        # if fecha_desde:
        #     piscinas = piscinas.filter(fecha_creacion__gte=fecha_desde)
        # if fecha_hasta:
        #     piscinas = piscinas.filter(fecha_creacion__lte=fecha_hasta)

        # Ordenar por empresa y orden
        piscinas = piscinas.order_by('empresa__nombre', 'orden')

        # Agrupar piscinas por empresa
        piscinas_por_empresa = OrderedDict()
        total_hectareas = 0
        total_activas = 0

        for piscina in piscinas:
            empresa_nombre = piscina.empresa.nombre if piscina.empresa else 'Sin Empresa'

            if empresa_nombre not in piscinas_por_empresa:
                piscinas_por_empresa[empresa_nombre] = []

            piscinas_por_empresa[empresa_nombre].append(piscina)

            # Calcular totales
            if piscina.hect:
                total_hectareas += float(piscina.hect)
            if piscina.estado:
                total_activas += 1

        # Fecha y hora actual para el reporte
        now = datetime.now()

        # Contexto
        context['nombre'] = 'Reporte de Piscinas'
        context['empresas'] = Empresa.objects.all().order_by('nombre')
        context['piscinas_por_empresa'] = piscinas_por_empresa
        context['total_piscinas'] = piscinas.count()
        context['total_hectareas'] = total_hectareas
        context['total_activas'] = total_activas
        context['fecha_desde'] = fecha_desde
        context['fecha_hasta'] = fecha_hasta
        context['empresa_seleccionada'] = empresa_id
        context['fecha_actual'] = now.strftime('%d/%m/%Y')
        context['hora_actual'] = now.strftime('%H:%M:%S')
        return context


# Piscinas de las Empresas
class listarPiscinasView(ListView):
    model = Piscinas
    template_name = 'app_empresa/app_piscinas/piscinas_listar.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Piscinas'
        context['piscinas'] = Piscinas.objects.all()
        context['empresa'] = Empresa.objects.all()
        return context


class crearPiscinaView(CreateView):
    model = Piscinas
    form_class = PiscinasForm
    template_name = 'app_empresa/app_piscinas/piscinas_crear.html'
    success_url = reverse_lazy('app_empresa:listar_piscinas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Ingresar Piscinas'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Piscina registrada correctamente')
        return super().form_valid(form)


class actualizarPiscinaView(UpdateView):
    model = Piscinas
    form_class = PiscinasForm
    template_name = 'app_empresa/app_piscinas/piscinas_crear.html'
    success_url = reverse_lazy('app_empresa:listar_piscinas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Piscina'
        return context


class eliminarPiscinaView(DeleteView):
    model = Piscinas
    form_class = PiscinasForm
    template_name = 'app_empresa/app_piscinas/piscinas_eliminar.html'
    success_url = reverse_lazy('app_empresa:listar_piscinas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Piscina'
        return context


class HistorialPiscinaView(ListView):
    model = PiscinaHistorial
    template_name = 'app_empresa/app_piscinas/historial_piscina.html'

    def get_queryset(self):
        return PiscinaHistorial.objects.filter(
            piscina_id=self.kwargs['pk']
        )


def historial_piscina_pdf(request, pk):
    piscina = get_object_or_404(Piscinas, pk=pk)

    historial = PiscinaHistorial.objects.filter(
        piscina=piscina
    ).order_by('-fecha_inicio')

    html = render_to_string(
        'app_empresa/app_piscinas/historial_pdf.html',
        {
            'piscina': piscina,
            'historial': historial
        }
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="historial_piscina.pdf"'
    HTML(string=html).write_pdf(response)

    return response

