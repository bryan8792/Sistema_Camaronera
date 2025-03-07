
import json
import os
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
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


class listarKardexGeneralView(ListView):
    model = Producto_Stock
    template_name = 'app_kardex/kardex_principal.html'

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
                # searchdata = Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],producto_empresa__nombre_empresa__siglas__icontains='PSM',activo__exact=True)
                searchdata = Producto_Stock.objects.all()
                for i in searchdata:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Kardex General de Movimientos'
        return context


class listarKardexDetalladoView(ListView):
    model = Producto_Stock
    template_name = 'app_kardex/kardex_detallado.html'

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
                # searchdata = Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],producto_empresa__nombre_empresa__siglas__icontains='PSM',activo__exact=True)
                searchdata = Producto_Stock.objects.filter(activo__exact=True)
                for i in searchdata:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Kardex Movimientos a Detalle'
        return context


class listarKardexMovimientosPSMView(ListView):
    model = Producto_Stock
    template_name = 'app_kardex/kardex_movimientos_psm.html'

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
                # searchdata = Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],producto_empresa__nombre_empresa__siglas__icontains='PSM',activo__exact=True)
                searchdata = Producto_Stock.objects.filter(producto_empresa__nombre_empresa__siglas__icontains='PSM',
                                                           activo__exact=True)
                for i in searchdata:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Kardex Movimientos a Detalle Empresa PSM'
        return context


class listarKardexMovimientosBIOView(ListView):
    model = Producto_Stock
    template_name = 'app_kardex/kardex_movimientos_bio.html'

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
                # searchdata = Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],producto_empresa__nombre_empresa__siglas__icontains='PSM',activo__exact=True)
                searchdata = Producto_Stock.objects.filter(producto_empresa__nombre_empresa__siglas__icontains='BIO',
                                                           activo__exact=True)
                for i in searchdata:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Kardex Movimientos a Detalle Empresa BIO'
        return context


class listarKardexProductosView(ListView):
    model = Producto_Stock
    template_name = 'app_kardex/kardex_productos.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_autocomplete_psm':
                data = []
                term = request.POST['term'].strip()
                empresa = request.POST['empresa']
                print('PSM')
                print(term)
                print(empresa)
                searchdata = Producto_Stock.objects.filter(producto_empresa__nombre_prod__nombre__icontains=term, activo__exact=True)
                if len(empresa):
                    searchdata = searchdata.filter(producto_empresa__nombre_empresa__siglas__icontains=empresa)
                for i in searchdata:
                    item = i.toJSON()
                    print(item)
                    data.append(item)
            # if action == 'search_autocomplete':
            #     print('entro')
            #     data = []
            #     term = request.POST['term'].strip()
            #     empresa = request.POST['empresa']
            #     searchdata = Producto_Stock.objects.filter(
            #         producto_empresa__nombre_prod__nombre__icontains=term,
            #         producto_empresa__nombre_empresa__siglas__contains=empresa, activo__exact=True)
            #     for i in searchdata:
            #         item = i.toJSON()
            #         print(item)
            #         data.append(item)
            elif action == 'search_autocomplete_bio':
                data = []
                term = request.POST['term'].strip()
                empresa = request.POST['empresa']
                print('BIO')
                print(term)
                print(empresa)
                searchdata = Producto_Stock.objects.filter(producto_empresa__nombre_prod__nombre__icontains=term, activo__exact=True)
                if len(empresa):
                    searchdata = searchdata.filter(producto_empresa__nombre_empresa__siglas__icontains=empresa)
                for i in searchdata:
                    item = i.toJSON()
                    print(item)
                    data.append(item)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Kardex de Movimientos Productos'
        return context
