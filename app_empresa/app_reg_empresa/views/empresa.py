from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from app_empresa.app_reg_empresa.forms import EmpresaForm
from app_empresa.app_reg_empresa.models import Empresa, Piscinas

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
    template_name = 'app_empresa/empresa_crear.html'
    success_url = reverse_lazy('app_empresa:listar_empresa')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Ingresar Empresa'
        return context


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


# Vista basada en clase
class listarEmpresaView(ListView):
    model = Empresa
    template_name = 'app_empresa/empresa_listar.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        #if request.method == 'GET':
            #return redirect('app_empresa:crear_empresa')
        return super().dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Empresa.objects.get(pk=request.POST['id']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Empresa'
        context['empresa'] = Empresa.objects.all()
        return context


