
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView
from app_dieta.app_dieta_reg.models import DetalleDiaDieta
from app_empresa.app_reg_empresa.models import Empresa
from app_inventario.app_categoria.models import Producto
from app_reportes.utils import render_to_pdf
from app_stock.app_detalle_stock.forms import ProdStockForm, ProdStockTotalForm
from app_stock.app_detalle_stock.models import Producto_Stock, Total_Stock, InvoiceStock
import decimal


# EMPRESA PRESQUERA SAN MIGUEL
class crearStockPSMView(CreateView):
    model = Producto_Stock
    form_class = ProdStockForm
    template_name = 'app_stock/stock_crear_psm.html'
    success_url = reverse_lazy('app_stock:listar_stock_psm')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos PSM'
        context['id_producto_empresa'] = self.kwargs['pk']
        producto = Total_Stock.objects.get(pk=self.kwargs['pk'])
        context['producto'] = producto
        context['movimientos'] = Producto_Stock.objects.all()

        unidad_aplicacion = producto.nombre_prod.unid_aplicacion  # LB   KG
        if unidad_aplicacion == 'GR':
            aplicacion = 1000
        elif unidad_aplicacion == 'KG':
            aplicacion = 2.2
        elif unidad_aplicacion == 'LB':
            aplicacion = 1
        else:
            aplicacion = 1000

        context['total'] = decimal.Decimal(aplicacion) * producto.nombre_prod.peso_presentacion

        return context


class listarStockPSMView(ListView):
    model = Total_Stock
    template_name = 'app_stock/stock_psm_listar.html'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos PSM'
        context['sotck'] = Total_Stock.objects.all()
        context['balanceados'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='BALANCEADOS', nombre_empresa__siglas='PSM')
        context['insumos'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='INSUMOS', nombre_empresa__siglas='PSM')
        return context


class listarStockUnicoPSMView(ListView):
    model = Producto_Stock
    template_name = 'app_stock/app_control/stock_unico_listar_psm.html'

    # def get_queryset(self):
    #     return Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'], activo__exact=True)

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
        context['nombre'] = 'Stock Productos PSM'
        return context


class listarStockPSMyBIOView(ListView):
    model = Total_Stock
    template_name = 'app_stock/stock_psmYbio_listar.html'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos General PSM&BIO'
        context['sotck'] = Total_Stock.objects.all()
        context['balanceados_psm'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='BALANCEADOS', nombre_empresa__siglas='PSM')
        context['insumos'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='INSUMOS', nombre_empresa__siglas='PSM')
        return context



class listarConsumoView(ListView):
    model = DetalleDiaDieta
    template_name = 'app_stock/stock_psm_listar.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = {}
        try:
            if 'pk' in kwargs:
                dieta = DetalleDiaDieta.objects.filter(dieta_id=kwargs['pk']).order_by('piscinas__orden')
                fecha_dieta = ''

                if dieta:
                    fecha_dieta = dieta[0].dieta.fecha

                # Empresa PSM
                balanceado = {}
                insumo = {}

                for b in dieta.filter(piscinas__empresa__siglas='PSM'):
                    if b.balanceado:
                        nombre_b = b.balanceado.nombre

                        if nombre_b not in balanceado:
                            balanceado[nombre_b] = b.cantidad
                        else:
                            balanceado[nombre_b] = balanceado[nombre_b] + b.cantidad

                    nombre_i = b.insumo1
                    if nombre_i:
                        nombre_i = Producto.objects.get(id=nombre_i).nombre
                        prod = Producto.objects.get(nombre__icontains=nombre_i).peso_presentacion
                        if nombre_i not in insumo:
                            insumo[nombre_i] = b.gramaje1
                        else:
                            insumo[nombre_i] = insumo[nombre_i] + b.gramaje1

                    nombre_i = b.insumo2
                    if nombre_i:
                        nombre_i = Producto.objects.get(id=nombre_i).nombre
                        prod = Producto.objects.get(nombre__icontains=nombre_i).peso_presentacion
                        if nombre_i not in insumo:
                            insumo[nombre_i] = b.gramaje2
                        else:
                            insumo[nombre_i] = insumo[nombre_i] + b.gramaje2

                    nombre_i = b.insumo3
                    if nombre_i:
                        nombre_i = Producto.objects.get(id=nombre_i).nombre
                        prod = Producto.objects.get(nombre__icontains=nombre_i).peso_presentacion
                        if nombre_i not in insumo:
                            insumo[nombre_i] = b.gramaje3
                        else:
                            insumo[nombre_i] = insumo[nombre_i] + b.gramaje3

                    nombre_i = b.insumo4
                    if nombre_i:
                        nombre_i = Producto.objects.get(id=nombre_i).nombre
                        prod = Producto.objects.get(nombre__icontains=nombre_i).peso_presentacion
                        if nombre_i not in insumo:
                            insumo[nombre_i] = b.gramaje4
                        else:
                            insumo[nombre_i] = insumo[nombre_i] + b.gramaje4

                resumen_totales = {
                    'psm': {'balanceado': balanceado, 'insumo': insumo}
                }

                # Empresa BIO
                balanceado = {}
                insumo = {}

                for b in dieta.filter(piscinas__empresa__siglas='BIO'):
                    if b.balanceado:
                        nombre_b = b.balanceado.nombre

                        if nombre_b not in balanceado:
                            balanceado[nombre_b] = b.cantidad
                        else:
                            balanceado[nombre_b] = balanceado[nombre_b] + b.cantidad

                    nombre_i = b.insumo1
                    if nombre_i:
                        nombre_i = Producto.objects.get(id=nombre_i).nombre
                        if nombre_i not in insumo:
                            insumo[nombre_i] = b.gramaje1
                        else:
                            insumo[nombre_i] = insumo[nombre_i] + b.gramaje1

                    nombre_i = b.insumo2
                    if nombre_i:
                        nombre_i = Producto.objects.get(id=nombre_i).nombre
                        if nombre_i not in insumo:
                            insumo[nombre_i] = b.gramaje2
                        else:
                            insumo[nombre_i] = insumo[nombre_i] + b.gramaje2

                    nombre_i = b.insumo3
                    if nombre_i:
                        nombre_i = Producto.objects.get(id=nombre_i).nombre
                        if nombre_i not in insumo:
                            insumo[nombre_i] = b.gramaje3
                        else:
                            insumo[nombre_i] = insumo[nombre_i] + b.gramaje3

                    nombre_i = b.insumo4
                    if nombre_i:
                        nombre_i = Producto.objects.get(id=nombre_i).nombre
                        if nombre_i not in insumo:
                            insumo[nombre_i] = b.gramaje4
                        else:
                            insumo[nombre_i] = insumo[nombre_i] + b.gramaje4

                resumen_totales['bio'] = {'balanceado': balanceado, 'insumo': insumo}

                data = {
                    'insumos': Producto.objects.filter(categoria__nombre__icontains='INSUMOS'),
                    'dieta_registros': dieta, 'fecha_dieta': fecha_dieta, 'resumen_totales': resumen_totales
                }
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos PSM'
        context['consumos_psm'] = Producto_Stock.objects.filter(tipo__icontains='EGRESO',
                                                                producto_empresa__nombre_empresa__siglas='PSM')
        return context


# EMPRESA BIO CASCAJAL
class crearStockBIOView(CreateView):
    model = Producto_Stock
    form_class = ProdStockForm
    template_name = 'app_stock/stock_crear_bio.html'
    success_url = reverse_lazy('app_stock:listar_stock_bio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos BIO'
        context['id_producto_empresa'] = self.kwargs['pk']
        producto = Total_Stock.objects.get(pk=self.kwargs['pk'])
        context['producto'] = producto

        unidad_aplicacion = producto.nombre_prod.unid_aplicacion  # LB   KG
        if unidad_aplicacion == 'GR':
            aplicacion = 1000
        elif unidad_aplicacion == 'KG':
            aplicacion = 2.2
        elif unidad_aplicacion == 'LB':
            aplicacion = 1
        else:
            aplicacion = 1000

        context['total'] = decimal.Decimal(aplicacion) * producto.nombre_prod.peso_presentacion

        return context


class listarStockBIOView(ListView):
    model = Total_Stock
    template_name = 'app_stock/stock_bio_listar.html'

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
        context['nombre'] = 'Stock Productos BIO'
        context['sotck'] = Total_Stock.objects.all()
        context['balanceados'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='BALANCEADOS',
                                                            nombre_empresa__siglas='BIO')
        context['insumos'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='INSUMOS',
                                                        nombre_empresa__siglas='BIO')
        return context


class listarStockUnicoBIOView(ListView):
    model = Producto_Stock
    template_name = 'app_stock/app_control/stock_unico_listar_bio.html'

    def get_queryset(self):
        return Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'], activo__exact=True)

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
        context['nombre'] = 'Stock Productos BIO'
        return context
