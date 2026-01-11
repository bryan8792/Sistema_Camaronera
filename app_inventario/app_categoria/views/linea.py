
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from app_inventario.app_categoria.forms import LineaForm
from app_inventario.app_categoria.models import Linea


# Lista basada en funcion
#def listarCategoria(request):
 #   data = {
 #       'nombre': 'Categoria',
 #       'categorias': Categoria.objects.all()
 #   }
 #   return render(request, 'app_inventario/app_categoria/cliente_listar.html', data)


#CREAREMOS EL INGRESO BASADO EN CLASES
class crearLineaView(CreateView):
    model = Linea
    form_class = LineaForm
    template_name = 'app_inventario/app_linea/linea_crear.html'
    success_url = reverse_lazy('app_categoria:listar_linea')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Ingresar Sub-Categoria'
        context['entity'] = 'Sub-Categoria'
        context['action'] = 'crear'
        return context


class actualizarLineaView(UpdateView):
    model = Linea
    form_class = LineaForm
    template_name = 'app_inventario/app_linea/linea_crear.html'
    success_url = reverse_lazy('app_categoria:listar_linea')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Sub-Categoria'
        context['entity'] = 'Sub-Categoria'
        context['action'] = 'crear'
        return context


class eliminarLineaView(DeleteView):
    model = Linea
    form_class = LineaForm
    template_name = 'app_inventario/app_linea/linea_eliminar.html'
    success_url = reverse_lazy('app_categoria:listar_linea')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Sub-Categoria'
        context['entity'] = 'Linea'
        context['action'] = 'crear'
        return context


#CREAREMOS LISTA BASADA EN CLASES
class listarLineaView(ListView):
    model = Linea
    template_name = 'app_inventario/app_linea/linea_listar.html'


    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Linea.objects.get(pk=request.POST['id']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Sub-Categoria'
        return context