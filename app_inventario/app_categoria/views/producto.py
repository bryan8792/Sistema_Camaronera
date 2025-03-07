
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from app_inventario.app_categoria.models import Categoria,Producto
from app_inventario.app_producto.forms import ProductoForm

def listarProducto(request):
    data = {
        'nombre': 'Producto',
        'categorias': Categoria.objects.all(),
        'productos': Producto.objects.all()
    }
    return render(request, 'app_inventario/app_producto/producto_listar.html', data)


# VISTA PARA CREAR EL PRODUCTO
class crearProductoView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'app_inventario/app_producto/producto_crear.html'
    success_url = reverse_lazy('app_categoria:listar_producto')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Registro de Producto'
        return context


# VISTAR PARA LISTAR EL PRODUCTO
class listarProductoView(ListView):
    # digo cual es el modelo o entidad en este caso categoria
    model = Producto
    # defino la plantilla
    template_name = 'app_inventario/app_producto/producto_listar.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Producto.objects.get(pk=request.POST['id']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #pongo el titulo a mi tabla y demas que necesiten
        context['nombre'] = 'Producto'
        context['categorias'] = Categoria.objects.all()
        context['productos'] = Producto.objects.all()
        return context


class actualizarProductoView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'app_inventario/app_producto/producto_crear.html'
    success_url = reverse_lazy('app_categoria:listar_producto')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Producto'
        context['entity'] = 'Producto'
        context['action'] = 'crear'
        return context


class eliminarProductoView(DeleteView):
    model = Producto
    form_class = ProductoForm
    template_name = 'app_inventario/app_producto/producto_eliminar.html'
    success_url = reverse_lazy('app_categoria:listar_producto')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Producto'
        context['entity'] = 'Producto'
        context['action'] = 'crear'
        return context