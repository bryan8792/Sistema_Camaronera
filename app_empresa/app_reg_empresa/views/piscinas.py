
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from app_empresa.app_piscinas.forms import PiscinasForm
from app_empresa.app_reg_empresa.forms import EmpresaForm
from app_empresa.app_reg_empresa.models import Empresa, Piscinas, PiscinaHistorial
from django.shortcuts import get_object_or_404


# Piscinas de las Empresas - aqio las listo abajo por clases hago lo mismo y es mejor abajo
def listarPiscina(request):
    data = {
        'nombre': 'Piscinas',
        'piscinas': Piscinas.objects.all(),
        'empresa': Empresa.objects.all()
    }
    return render(request, 'app_empresa/app_piscinas/piscinas_listar.html', data)


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

