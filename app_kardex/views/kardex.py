
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


# class listarKardexGeneralView(ListView):
#     model = Producto_Stock
#     template_name = 'app_kardex/kardex_principal.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == 'searchdata':
#                 data = []
#                 # searchdata = Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],producto_empresa__nombre_empresa__siglas__icontains='PSM',activo__exact=True)
#                 searchdata = Producto_Stock.objects.all()
#                 for i in searchdata:
#                     data.append(i.toJSON())
#             else:
#                 data['error'] = 'Ha ocurrido un error'
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data, safe=False)
#
#     # defino el dicionario para enviar variables a mi plantilla
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Kardex General de Movimientos'
#         return context
#
#
# class listarKardexDetalladoView(ListView):
#     model = Producto_Stock
#     template_name = 'app_kardex/kardex_detallado.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == 'searchdata':
#                 data = []
#                 # searchdata = Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],producto_empresa__nombre_empresa__siglas__icontains='PSM',activo__exact=True)
#                 searchdata = Producto_Stock.objects.filter(activo__exact=True)
#                 for i in searchdata:
#                     data.append(i.toJSON())
#             else:
#                 data['error'] = 'Ha ocurrido un error'
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data, safe=False)
#
#     # defino el dicionario para enviar variables a mi plantilla
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Kardex Movimientos a Detalle'
#         return context
#
#
# class listarKardexMovimientosPSMView(ListView):
#     model = Producto_Stock
#     template_name = 'app_kardex/kardex_movimientos_psm.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == 'searchdata':
#                 data = []
#                 # searchdata = Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],producto_empresa__nombre_empresa__siglas__icontains='PSM',activo__exact=True)
#                 searchdata = Producto_Stock.objects.filter(producto_empresa__nombre_empresa__siglas__icontains='PSM',
#                                                            activo__exact=True)
#                 for i in searchdata:
#                     data.append(i.toJSON())
#             else:
#                 data['error'] = 'Ha ocurrido un error'
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data, safe=False)
#
#     # defino el dicionario para enviar variables a mi plantilla
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Kardex Movimientos a Detalle Empresa PSM'
#         return context
#
#
# class listarKardexMovimientosBIOView(ListView):
#     model = Producto_Stock
#     template_name = 'app_kardex/kardex_movimientos_bio.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == 'searchdata':
#                 data = []
#                 # searchdata = Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],producto_empresa__nombre_empresa__siglas__icontains='PSM',activo__exact=True)
#                 searchdata = Producto_Stock.objects.filter(producto_empresa__nombre_empresa__siglas__icontains='BIO',
#                                                            activo__exact=True)
#                 for i in searchdata:
#                     data.append(i.toJSON())
#             else:
#                 data['error'] = 'Ha ocurrido un error'
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data, safe=False)
#
#     # defino el dicionario para enviar variables a mi plantilla
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Kardex Movimientos a Detalle Empresa BIO'
#         return context
#
#
# class listarKardexProductosView(ListView):
#     model = Producto_Stock
#     template_name = 'app_kardex/kardex_productos.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == 'search_autocomplete_psm':
#                 data = []
#                 term = request.POST['term'].strip()
#                 empresa = request.POST['empresa']
#                 print('PSM')
#                 print(term)
#                 print(empresa)
#                 searchdata = Producto_Stock.objects.filter(producto_empresa__nombre_prod__nombre__icontains=term, activo__exact=True)
#                 if len(empresa):
#                     searchdata = searchdata.filter(producto_empresa__nombre_empresa__siglas__icontains=empresa)
#                 for i in searchdata:
#                     item = i.toJSON()
#                     print(item)
#                     data.append(item)
#             # if action == 'search_autocomplete':
#             #     print('entro')
#             #     data = []
#             #     term = request.POST['term'].strip()
#             #     empresa = request.POST['empresa']
#             #     searchdata = Producto_Stock.objects.filter(
#             #         producto_empresa__nombre_prod__nombre__icontains=term,
#             #         producto_empresa__nombre_empresa__siglas__contains=empresa, activo__exact=True)
#             #     for i in searchdata:
#             #         item = i.toJSON()
#             #         print(item)
#             #         data.append(item)
#             elif action == 'search_autocomplete_bio':
#                 data = []
#                 term = request.POST['term'].strip()
#                 empresa = request.POST['empresa']
#                 print('BIO')
#                 print(term)
#                 print(empresa)
#                 searchdata = Producto_Stock.objects.filter(producto_empresa__nombre_prod__nombre__icontains=term, activo__exact=True)
#                 if len(empresa):
#                     searchdata = searchdata.filter(producto_empresa__nombre_empresa__siglas__icontains=empresa)
#                 for i in searchdata:
#                     item = i.toJSON()
#                     print(item)
#                     data.append(item)
#             else:
#                 data['error'] = 'Ha ocurrido un error'
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data, safe=False)
#
#     # defino el dicionario para enviar variables a mi plantilla
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Kardex de Movimientos Productos'
#         return context




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
            action = request.POST.get('action', '')
            if action == 'searchdata':
                draw = int(request.POST.get('draw', 1))
                start = int(request.POST.get('start', 0))
                length = int(request.POST.get('length', 50))
                search_value = request.POST.get('search[value]', '')

                queryset = Producto_Stock.objects.select_related(
                    'producto_empresa',
                    'producto_empresa__nombre_empresa',
                    'producto_empresa__nombre_prod'
                )

                total_records = queryset.count()

                if search_value:
                    queryset = queryset.filter(
                        Q(producto_empresa__nombre_prod__nombre__icontains=search_value) |
                        Q(producto_empresa__nombre_empresa__siglas__icontains=search_value) |
                        Q(numero_guia__icontains=search_value) |
                        Q(piscinas__icontains=search_value)
                    )

                filtered_records = queryset.count()
                queryset = queryset.order_by('-fecha_ingreso')[start:start + length]

                data_list = []
                for item in queryset:
                    data_list.append(item.toJSON())

                return JsonResponse({
                    'draw': draw,
                    'recordsTotal': total_records,
                    'recordsFiltered': filtered_records,
                    'data': data_list
                })
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

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
            action = request.POST.get('action', '')
            if action == 'searchdata':
                draw = int(request.POST.get('draw', 1))
                start = int(request.POST.get('start', 0))
                length = int(request.POST.get('length', 50))
                search_value = request.POST.get('search[value]', '')

                queryset = Producto_Stock.objects.select_related(
                    'producto_empresa',
                    'producto_empresa__nombre_empresa',
                    'producto_empresa__nombre_prod'
                ).filter(activo__exact=True)

                total_records = queryset.count()

                if search_value:
                    queryset = queryset.filter(
                        Q(producto_empresa__nombre_prod__nombre__icontains=search_value) |
                        Q(producto_empresa__nombre_empresa__siglas__icontains=search_value) |
                        Q(numero_guia__icontains=search_value) |
                        Q(piscinas__icontains=search_value)
                    )

                filtered_records = queryset.count()
                queryset = queryset.order_by('-fecha_ingreso')[start:start + length]

                data_list = []
                for item in queryset:
                    data_list.append(item.toJSON())

                return JsonResponse({
                    'draw': draw,
                    'recordsTotal': total_records,
                    'recordsFiltered': filtered_records,
                    'data': data_list
                })
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

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
            action = request.POST.get('action', '')
            if action == 'searchdata':
                draw = int(request.POST.get('draw', 1))
                start = int(request.POST.get('start', 0))
                length = int(request.POST.get('length', 50))
                search_value = request.POST.get('search[value]', '')

                queryset = Producto_Stock.objects.select_related(
                    'producto_empresa',
                    'producto_empresa__nombre_empresa',
                    'producto_empresa__nombre_prod'
                ).filter(
                    producto_empresa__nombre_empresa__siglas__icontains='PSM',
                    activo__exact=True
                )

                total_records = queryset.count()

                if search_value:
                    queryset = queryset.filter(
                        Q(producto_empresa__nombre_prod__nombre__icontains=search_value) |
                        Q(numero_guia__icontains=search_value) |
                        Q(piscinas__icontains=search_value)
                    )

                filtered_records = queryset.count()
                queryset = queryset.order_by('-fecha_ingreso')[start:start + length]

                data_list = []
                for item in queryset:
                    data_list.append(item.toJSON())

                return JsonResponse({
                    'draw': draw,
                    'recordsTotal': total_records,
                    'recordsFiltered': filtered_records,
                    'data': data_list
                })
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

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
            action = request.POST.get('action', '')
            if action == 'searchdata':
                draw = int(request.POST.get('draw', 1))
                start = int(request.POST.get('start', 0))
                length = int(request.POST.get('length', 50))
                search_value = request.POST.get('search[value]', '')

                queryset = Producto_Stock.objects.select_related(
                    'producto_empresa',
                    'producto_empresa__nombre_empresa',
                    'producto_empresa__nombre_prod'
                ).filter(
                    producto_empresa__nombre_empresa__siglas__icontains='BIO',
                    activo__exact=True
                )

                total_records = queryset.count()

                if search_value:
                    queryset = queryset.filter(
                        Q(producto_empresa__nombre_prod__nombre__icontains=search_value) |
                        Q(numero_guia__icontains=search_value) |
                        Q(piscinas__icontains=search_value)
                    )

                filtered_records = queryset.count()
                queryset = queryset.order_by('-fecha_ingreso')[start:start + length]

                data_list = []
                for item in queryset:
                    data_list.append(item.toJSON())

                return JsonResponse({
                    'draw': draw,
                    'recordsTotal': total_records,
                    'recordsFiltered': filtered_records,
                    'data': data_list
                })
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

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
            action = request.POST.get('action', '')

            if action == 'search_autocomplete':
                data = []
                term = request.POST.get('term', '').strip()

                searchdata = Producto_Stock.objects.select_related(
                    'producto_empresa',
                    'producto_empresa__nombre_empresa',
                    'producto_empresa__nombre_prod'
                ).filter(
                    producto_empresa__nombre_prod__nombre__icontains=term,
                    activo__exact=True
                ).values(
                    'producto_empresa__nombre_prod__nombre'
                ).distinct()[:20]

                for i in searchdata:
                    data.append({
                        'id': i['producto_empresa__nombre_prod__nombre'],
                        'text': i['producto_empresa__nombre_prod__nombre'],
                        'value': i['producto_empresa__nombre_prod__nombre']
                    })

            elif action == 'search_producto_psm':
                data = []
                nombre_producto = request.POST.get('nombre_producto', '').strip()

                queryset = Producto_Stock.objects.select_related(
                    'producto_empresa',
                    'producto_empresa__nombre_empresa',
                    'producto_empresa__nombre_prod'
                ).filter(
                    producto_empresa__nombre_prod__nombre__iexact=nombre_producto,
                    producto_empresa__nombre_empresa__siglas__icontains='PSM',
                    activo__exact=True
                ).order_by('-fecha_ingreso')[:200]

                for i in queryset:
                    data.append(i.toJSON())

            elif action == 'search_producto_bio':
                data = []
                nombre_producto = request.POST.get('nombre_producto', '').strip()

                queryset = Producto_Stock.objects.select_related(
                    'producto_empresa',
                    'producto_empresa__nombre_empresa',
                    'producto_empresa__nombre_prod'
                ).filter(
                    producto_empresa__nombre_prod__nombre__iexact=nombre_producto,
                    producto_empresa__nombre_empresa__siglas__icontains='BIO',
                    activo__exact=True
                ).order_by('-fecha_ingreso')[:200]

                for i in queryset:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Kardex de Movimientos Productos'
        return context
