
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
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from collections import defaultdict
from django.db.models.functions import TruncMonth, ExtractYear
from decimal import Decimal


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



class listarProductosEmpresaView(ListView):
    """Vista para mostrar productos con stock por empresa (PSM y BIO)"""
    model = Total_Stock
    template_name = 'app_kardex/productos_empresa.html'

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

                # Obtener productos unicos
                from django.db.models import Q

                productos = Producto.objects.filter(estado=True).select_related('categoria', 'descripcion')

                total_records = productos.count()

                if search_value:
                    productos = productos.filter(
                        Q(nombre__icontains=search_value) |
                        Q(categoria__nombre__icontains=search_value)
                    )

                filtered_records = productos.count()
                productos = productos.order_by('nombre')[start:start + length]

                data_list = []
                for producto in productos:
                    # Obtener stock PSM
                    stock_psm = Total_Stock.objects.filter(
                        nombre_prod=producto,
                        nombre_empresa__siglas__icontains='PSM'
                    ).aggregate(total=Sum('stock'))['total'] or 0

                    # Obtener stock BIO
                    stock_bio = Total_Stock.objects.filter(
                        nombre_prod=producto,
                        nombre_empresa__siglas__icontains='BIO'
                    ).aggregate(total=Sum('stock'))['total'] or 0

                    # Codigo del producto
                    codigo = f"A{producto.id}"

                    data_list.append({
                        'id': producto.id,
                        'nombre': producto.nombre,
                        'codigo': codigo,
                        'stock_psm': float(stock_psm),
                        'stock_bio': float(stock_bio),
                        'stock_total': float(stock_psm) + float(stock_bio),
                        'unid_medida': producto.unid_medida or '',
                        'presentacion': producto.presentacion or '',
                        'peso_presentacion': float(producto.peso_presentacion) if producto.peso_presentacion else 0,
                        'unidad_presentacion': f"{producto.peso_presentacion or ''} {producto.unid_medida or ''} / {producto.presentacion or ''}".strip()
                    })

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
        context['nombre'] = 'Productos por Empresa - Stock Total'
        return context



class listarMovimientosPorProductoView(ListView):
    """Vista para mostrar movimientos agrupados por mes y producto (tabla pivot)"""
    model = Producto_Stock
    template_name = 'app_kardex/movimientos_por_producto.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action', '')

            if action == 'searchdata':
                empresa = request.POST.get('empresa', '')
                anio = request.POST.get('anio', '')

                # Meses en espanol
                MESES_ESPANOL = {
                    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
                }

                # Filtrar movimientos - solo egresos (consumos)
                queryset = Producto_Stock.objects.select_related(
                    'producto_empresa',
                    'producto_empresa__nombre_empresa',
                    'producto_empresa__nombre_prod'
                ).filter(
                    activo=True
                ).exclude(
                    piscinas__exact='Todas las Piscinas'
                )

                if empresa:
                    queryset = queryset.filter(
                        producto_empresa__nombre_empresa__siglas__icontains=empresa
                    )

                if anio:
                    queryset = queryset.filter(fecha_ingreso__year=int(anio))

                # Obtener lista de productos unicos ordenados alfabeticamente
                productos_unicos = list(queryset.values_list(
                    'producto_empresa__nombre_prod__nombre', flat=True
                ).distinct().order_by('producto_empresa__nombre_prod__nombre'))

                # Agrupar por mes y producto - sumar egresos
                movimientos = queryset.annotate(
                    mes=TruncMonth('fecha_ingreso')
                ).values(
                    'mes',
                    'producto_empresa__nombre_prod__nombre'
                ).annotate(
                    total_egreso=Sum('cantidad_egreso')
                ).order_by('mes', 'producto_empresa__nombre_prod__nombre')

                # Obtener meses unicos ordenados
                meses_unicos = list(queryset.annotate(
                    mes=TruncMonth('fecha_ingreso')
                ).values_list('mes', flat=True).distinct().order_by('mes'))

                # Construir matriz de datos
                matriz = defaultdict(lambda: defaultdict(float))
                for mov in movimientos:
                    if mov['mes']:
                        mes_str = MESES_ESPANOL.get(mov['mes'].month, str(mov['mes'].month))
                        producto = mov['producto_empresa__nombre_prod__nombre']
                        valor = float(mov['total_egreso'] or 0)
                        matriz[mes_str][producto] += valor

                # Convertir a formato para la tabla
                data_list = []
                totales_por_producto = defaultdict(float)

                for mes in meses_unicos:
                    if mes:
                        mes_str = MESES_ESPANOL.get(mes.month, str(mes.month))
                        row = {'mes': mes_str}
                        for producto in productos_unicos:
                            valor = matriz[mes_str].get(producto, 0)
                            row[producto] = round(valor, 2)  # Mantener 2 decimales
                            totales_por_producto[producto] += valor
                        data_list.append(row)

                # Agregar fila de totales
                row_total = {'mes': 'Total general'}
                for producto in productos_unicos:
                    row_total[producto] = round(totales_por_producto[producto], 2)
                data_list.append(row_total)

                return JsonResponse({
                    'productos': productos_unicos,
                    'data': data_list
                })

            elif action == 'get_anios':
                # Obtener anos disponibles
                anios = Producto_Stock.objects.filter(
                    activo=True
                ).annotate(
                    anio=ExtractYear('fecha_ingreso')
                ).values_list('anio', flat=True).distinct()

                data = sorted(list(set([a for a in anios if a])), reverse=True)

            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Movimientos por Producto'
        return context




class listarKardexProductosEmpresasView(ListView):
    """Vista para Kardex de Movimientos por Producto - PSM y BIO lado a lado"""
    model = Producto_Stock
    template_name = 'app_kardex/kardex_productos_empresas.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action', '')

            if action == 'search_autocomplete':
                # Buscar productos para el autocomplete
                data = []
                term = request.POST.get('term', '').strip()

                if len(term) >= 2:
                    # Obtener productos unicos que coincidan
                    productos = Producto_Stock.objects.select_related(
                        'producto_empresa__nombre_prod'
                    ).filter(
                        producto_empresa__nombre_prod__nombre__icontains=term,
                        activo=True
                    ).values(
                        'producto_empresa__nombre_prod__nombre',
                        'producto_empresa__nombre_prod__id'
                    ).distinct()[:20]

                    for p in productos:
                        data.append({
                            'id': p['producto_empresa__nombre_prod__id'],
                            'text': p['producto_empresa__nombre_prod__nombre'],
                            'value': p['producto_empresa__nombre_prod__nombre']
                        })

            elif action == 'search_producto_psm':
                # Buscar movimientos del producto en PSM
                data = []
                nombre_producto = request.POST.get('nombre_producto', '').strip()

                if nombre_producto:
                    queryset = Producto_Stock.objects.select_related(
                        'producto_empresa',
                        'producto_empresa__nombre_empresa',
                        'producto_empresa__nombre_prod'
                    ).filter(
                        producto_empresa__nombre_prod__nombre__iexact=nombre_producto,
                        producto_empresa__nombre_empresa__siglas__icontains='PSM',
                        activo=True
                    ).order_by('fecha_ingreso', 'id')

                    # Calcular saldo acumulado
                    saldo_acumulado = Decimal('0.00')
                    total_ingreso = Decimal('0.00')
                    total_egreso = Decimal('0.00')

                    for item in queryset:
                        ingreso = Decimal(str(item.cantidad_ingreso or 0))
                        egreso = Decimal(str(item.cantidad_egreso or 0))
                        saldo_acumulado = saldo_acumulado + ingreso - egreso
                        total_ingreso += ingreso
                        total_egreso += egreso

                        data.append({
                            'id': item.id,
                            'fecha_ingreso': item.fecha_ingreso.strftime('%d/%m/%Y') if item.fecha_ingreso else '',
                            'proveedor': item.responsable_ingreso or '',
                            'cantidad_ingreso': float(ingreso),
                            'cantidad_egreso': float(egreso),
                            'saldo': float(saldo_acumulado),
                            'producto_nombre': item.producto_empresa.nombre_prod.nombre if item.producto_empresa and item.producto_empresa.nombre_prod else ''
                        })

                    # Obtener stock actual
                    stock_actual = Total_Stock.objects.filter(
                        nombre_prod__nombre__iexact=nombre_producto,
                        nombre_empresa__siglas__icontains='PSM'
                    ).aggregate(total=Sum('stock'))['total'] or 0

                    return JsonResponse({
                        'data': data,
                        'total_ingreso': float(total_ingreso),
                        'total_egreso': float(total_egreso),
                        'saldo_final': float(saldo_acumulado),
                        'stock_actual': float(stock_actual)
                    })

            elif action == 'search_producto_bio':
                # Buscar movimientos del producto en BIO
                data = []
                nombre_producto = request.POST.get('nombre_producto', '').strip()

                if nombre_producto:
                    queryset = Producto_Stock.objects.select_related(
                        'producto_empresa',
                        'producto_empresa__nombre_empresa',
                        'producto_empresa__nombre_prod'
                    ).filter(
                        producto_empresa__nombre_prod__nombre__iexact=nombre_producto,
                        producto_empresa__nombre_empresa__siglas__icontains='BIO',
                        activo=True
                    ).order_by('fecha_ingreso', 'id')

                    # Calcular saldo acumulado
                    saldo_acumulado = Decimal('0.00')
                    total_ingreso = Decimal('0.00')
                    total_egreso = Decimal('0.00')

                    for item in queryset:
                        ingreso = Decimal(str(item.cantidad_ingreso or 0))
                        egreso = Decimal(str(item.cantidad_egreso or 0))
                        saldo_acumulado = saldo_acumulado + ingreso - egreso
                        total_ingreso += ingreso
                        total_egreso += egreso

                        data.append({
                            'id': item.id,
                            'fecha_ingreso': item.fecha_ingreso.strftime('%d/%m/%Y') if item.fecha_ingreso else '',
                            'proveedor': item.responsable_ingreso or '',
                            'cantidad_ingreso': float(ingreso),
                            'cantidad_egreso': float(egreso),
                            'saldo': float(saldo_acumulado),
                            'producto_nombre': item.producto_empresa.nombre_prod.nombre if item.producto_empresa and item.producto_empresa.nombre_prod else ''
                        })

                    # Obtener stock actual
                    stock_actual = Total_Stock.objects.filter(
                        nombre_prod__nombre__iexact=nombre_producto,
                        nombre_empresa__siglas__icontains='BIO'
                    ).aggregate(total=Sum('stock'))['total'] or 0

                    return JsonResponse({
                        'data': data,
                        'total_ingreso': float(total_ingreso),
                        'total_egreso': float(total_egreso),
                        'saldo_final': float(saldo_acumulado),
                        'stock_actual': float(stock_actual)
                    })
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Kardex de Movimientos Productos'
        return context