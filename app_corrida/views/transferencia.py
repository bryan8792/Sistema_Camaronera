
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


class crearTransferenciaView(CreateView):
    model = Producto_Stock
    form_class = ProdStockForm
    template_name = 'app_corrida/app_transferencia/transferencia_crear.html'
    success_url = reverse_lazy('app_corrida:listar_transferencia')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Producto a Utilizar en la Transferencia'
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


class listarTransferenciaView(ListView):
    model = Total_Stock
    template_name = 'app_corrida/app_transferencia/transferencia_listar.html'

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
        context['producto'] = Total_Stock.objects.filter(nombre_empresa__siglas='PSM')
        #context['insumos'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='INSUMOS', nombre_empresa__siglas='PSM')
        return context