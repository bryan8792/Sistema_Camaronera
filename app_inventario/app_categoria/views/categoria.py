
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from app_inventario.app_categoria.forms import CategoriaForm
from app_inventario.app_categoria.models import Categoria


# Lista basada en funcion
#def listarCategoria(request):
 #   data = {
 #       'nombre': 'Categoria',
 #       'categorias': Categoria.objects.all()
 #   }
 #   return render(request, 'app_inventario/app_categoria/categoria_listar.html', data)


#CREAREMOS EL INGRESO BASADO EN CLASES
class crearCategoriaView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'app_inventario/app_categoria/categoria_crear.html'
    success_url = reverse_lazy('app_categoria:listar_categoria')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Ingresar Categoría'
        context['entity'] = 'Categoría'
        context['action'] = 'crear'
        return context


class actualizarCategoriaView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'app_inventario/app_categoria/categoria_crear.html'
    success_url = reverse_lazy('app_categoria:listar_categoria')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Categoría'
        context['entity'] = 'Categoría'
        context['action'] = 'crear'
        return context


class eliminarCategoriaView(DeleteView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'app_inventario/app_categoria/categoria_eliminar.html'
    success_url = reverse_lazy('app_categoria:listar_categoria')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Categoría'
        context['entity'] = 'Categoría'
        context['action'] = 'crear'
        return context


#CREAREMOS LISTA BASADA EN CLASES
class listarCategoriaView(ListView):
    # digo cual es el modelo o entidad en este caso categoria
    model = Categoria
    # defino la plantilla
    template_name = 'app_inventario/app_categoria/categoria_listar.html'


    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Categoria.objects.get(pk=request.POST['id']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #pongo el titulo a mi tabla y demas que necesiten
        context['nombre'] = 'Categoría'
        return context