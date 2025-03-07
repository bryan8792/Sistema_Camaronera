
import decimal
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from app_empresa.app_reg_empresa.models import Empresa
from app_inventario.app_categoria.models import Producto
from app_stock.app_detalle_stock.forms import ProdStockForm, ProdStockTotalForm
from app_stock.app_detalle_stock.models import Producto_Stock, Total_Stock


# EMPRESA PRESQUERA SAN MIGUEL
class crearStockPSMDirectoView(CreateView):
    model = Producto_Stock
    form_class = ProdStockForm
    template_name = 'app_stock_directo/stock_dir_crear_psm.html'
    success_url = reverse_lazy('app_stock_directo:listar_stock_directo_psm')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos Aplicación Directa PSM'
        context['id_producto_empresa'] = self.kwargs['pk']
        producto = Total_Stock.objects.get(pk=self.kwargs['pk'])
        context['producto'] = producto

        unidad_aplicacion = producto.nombre_prod.unid_aplicacion
        print('LA APLICACION ES  '+unidad_aplicacion)
        if unidad_aplicacion == 'GR':
            aplicacion = 1000
        elif unidad_aplicacion == 'KG':
            aplicacion = 2.2
        elif unidad_aplicacion == 'CA':
            aplicacion = 1
        elif unidad_aplicacion == 'LB':
            aplicacion = 55
        else:
            aplicacion = 1000

        context['unidad_aplicacion'] = producto.nombre_prod.unid_aplicacion
        context['aplicacion'] = aplicacion
        context['peso_presentacion'] = producto.nombre_prod.peso_presentacion
        context['nombre_presentacion'] = producto.nombre_prod.nombre
        context['total'] = decimal.Decimal(aplicacion) * producto.nombre_prod.peso_presentacion
        return context


class listarStockPSMDirectoView(ListView):
    model = Total_Stock
    template_name = 'app_stock_directo/stock_dir_listar_psm.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Total_Stock.objects.get(pk=request.POST['id']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos Aplicación Directa PSM'
        context['sotck'] = Total_Stock.objects.all()
        context['balanceados'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='BALANCEADOS', nombre_empresa__siglas='PSM')
        # context['insumos'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='INSUMOS', nombre_empresa__siglas='PSM')
        context['insumos'] = Total_Stock.objects.filter(nombre_empresa__siglas='PSM')
        return context


class listarStockUnicoPSMDirectoView(ListView):
    model = Producto_Stock
    template_name = 'app_stock_directo/app_control/stock_unico_directo_listar_psm.html'

    # def get_queryset(self):
    #     return Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'], activo__exact=True)
    #     # return Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],
    #     #                                      producto_empresa__nombre_empresa__siglas__icontains='PSM',
    #     #                                      activo__exact=True)

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],
                                                       producto_empresa__nombre_empresa__siglas__icontains='PSM',
                                                       activo__exact=True):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos Aplicación Directa PSM'
        return context



# EMPRESA BIO CASCAJAL
class crearStockBIODirectoView(CreateView):
    model = Producto_Stock
    form_class = ProdStockForm
    template_name = 'app_stock_directo/stock_dir_crear_bio.html'
    success_url = reverse_lazy('app_stock_directo:listar_stock_directo_bio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos Aplicación Directa BIO'
        context['id_producto_empresa'] = self.kwargs['pk']
        producto = Total_Stock.objects.get(pk=self.kwargs['pk'])
        context['producto'] = producto

        unidad_aplicacion = producto.nombre_prod.unid_aplicacion
        if unidad_aplicacion == 'GR':
            aplicacion = 1000
        elif unidad_aplicacion == 'KG':
            aplicacion = 2.2
        elif unidad_aplicacion == 'LB':
            aplicacion = 55
        else:
            aplicacion = 1000

        context['aplicacion'] = aplicacion
        context['peso_presentacion'] = producto.nombre_prod.peso_presentacion

        return context

class listarStockBIODirectoView(ListView):
    model = Total_Stock
    template_name = 'app_stock_directo/stock_dir_listar_bio.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Total_Stock.objects.get(pk=request.POST['id']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos Aplicación Directa BIO'
        context['sotck'] = Total_Stock.objects.all()
        context['balanceados'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='BALANCEADOS', nombre_empresa__siglas='BIO')
        context['insumos'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='INSUMOS', nombre_empresa__siglas='BIO')
        return context

class listarStockUnicoBIODirectoView(ListView):
    model = Producto_Stock
    template_name = 'app_stock_directo/app_control/stock_unico_listar_bio.html'

    def get_queryset(self):
        return Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],
                                             producto_empresa__nombre_empresa__siglas__icontains='BIO',
                                             activo__exact=True)

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Producto_Stock.objects.get(producto_empresa_id=self.kwargs['pk']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos Aplicación Directa BIO'
        return context