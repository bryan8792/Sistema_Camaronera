
import json
import os
from itertools import groupby

from click.core import F
from django.conf import settings
from django.db import transaction
from django.forms import models
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponseRedirect
from django.template.loader import get_template
import decimal
from django.contrib.auth.decorators import login_required
from weasyprint import HTML, CSS
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from app_corrida.forms import PrecSiembraCuerpForm
from app_corrida.models import PrecSiembraCuerp, PrecSiembraEnc
from app_empresa.app_reg_empresa.models import Piscinas
from app_inventario.app_categoria.models import Producto
from app_stock.app_detalle_stock.models import Producto_Stock, Total_Stock
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count
from app_corrida.forms import ReportForm
import pandas as pd
#from datatable import (dt, f, by, ifelse, update, sort, count, min, max, mean, sum, rowsum)


class reportSiembraPDF(View):
    def get(self, request, *args, **kwargs):
        try:
            template = get_template('app_reportes/report_siembra.html')
            detalle_cuerpo = PrecSiembraCuerp.objects.filter(fecha_registro_id=self.kwargs['pk'])

            fecha = '',
            observacion = '',
            prod_cantidad = '',
            resul_oper = ''

            if detalle_cuerpo:
                fecha = detalle_cuerpo[0].fecha_registro.fecha_registro
                observacion = detalle_cuerpo[0].fecha_registro.observacion
                prod_cantidad = detalle_cuerpo[0].fecha_registro.prod_cantidad
                resul_oper = detalle_cuerpo[0].fecha_registro.resul_oper

            context = {
                'sale': PrecSiembraEnc.objects.filter(pk=self.kwargs['pk']),
                'comp': {'comprobante': 'HISTORIAL DE CONSUMO - CRIA DE CAMARON'},
                'detalle_cuerpo': detalle_cuerpo,
                'fecha': fecha,
                'observacion': observacion,
                'prod_cantidad': prod_cantidad,
                'resul_oper': resul_oper,
            }

            html = template.render(context)
            css_url = os.path.join(settings.BASE_DIR, 'static/lib/bootstrap-4.4.1-dist/css/bootstrap.min.css')
            pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(css_url)])
            return HttpResponse(pdf, content_type='application/pdf')
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('app_corrida:listar_siembra'))


class listarSiembraCuantificableView(ListView):
    model = PrecSiembraEnc
    template_name = 'app_corrida/app_siembra/app_siembra_cuantificable/listar_siembra.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata_cuant':
                data = []
                for i in PrecSiembraEnc.objects.filter(tip_precSiembra__exact=True):
                    data.append(i.toJSON())
            elif action == 'searchdata_val':
                data = []
                for i in PrecSiembraEnc.objects.filter(tip_precSiembra__exact=False):
                    data.append(i.toJSON())
            elif action == 'search_details_enc':
                data = []
                for i in PrecSiembraEnc.objects.filter(id=request.POST['id']):
                    data.append(i.toJSON())
            elif action == 'search_details_cuerp':
                data = []
                for i in PrecSiembraCuerp.objects.filter(fecha_registro_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Siembras Precias Cuantificable - Valorizable'
        context['title'] = 'Listado de Siembras de Precias'
        context['list_url'] = reverse_lazy('app_factura:listar_factura')
        context['entity'] = 'Siembras Precias'
        return context


class crearSiembraCuantificableView(CreateView):
    model = PrecSiembraCuerp
    form_class = PrecSiembraCuerpForm
    template_name = 'app_corrida/app_siembra/app_siembra_cuantificable/crear_siembra.html'
    success_url = reverse_lazy('app_dieta:principal_dia')
    url_redirect = success_url

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = []
                ids_exclude_pro = json.loads(request.POST['ids'])
                queryset_prod = Producto.objects.all().exclude(id__in=ids_exclude_pro)
                for i in queryset_prod:
                    item = i.toJSON()
                    item['prod_cantidad'] = 0
                    data.append(item)
            # elif action == 'search_rango':
            #     data = []
            #     start_date = request.POST.get('start_date', '')
            #     end_date = request.POST.get('end_date', '')
            #     searchdata = Producto_Stock.objects.filter(piscinas__exact=Piscinas.objects.get(id=15), activo__exact=True).order_by('producto_empresa_id').distinct().values_list('producto_empresa_id', flat=True)
            #     print('OBTENIENDO TOTAL DE: searchdata')
            #     print(searchdata)
            #     # for i in Total_Stock.objects.filter(id__in=list(searchdata)):
            #     for i in Producto_Stock.objects.filter(producto_empresa_id__in=list(searchdata), piscinas__exact=Piscinas.objects.get(id=15), activo__exact=True, fecha_ingreso__range=[start_date, end_date]):
            #         print('OBTENIENDO TOTAL DE: i')
            #         print(i.id)
            #         # queryset = Producto_Stock.objects.filter(producto_empresa_id=i.id, piscinas__exact=Piscinas.objects.get(id=15), activo__exact=True, fecha_ingreso__range=[start_date, end_date])
            #
            #         data.append([
            #             i.producto_empresa.nombre_prod.nombre,
            #             i.piscinas,
            #             format(i.cantidad_egreso, '.2f'),
            #             format(i.producto_empresa.nombre_prod.costo, '.10f'),
            #             format(i.producto_empresa.nombre_prod.costo, '.10f'),
            #         ])
            #
            #         # if queryset.exists():
            #         #     item = queryset[0]
            #         #     print('queryset')
            #         #     print(queryset[0])
            #         #
            #         #     print('----------------------------------- EL VALOR DE ITEM -----------------------------------')
            #         #
            #         #     data.append([
            #         #         item.producto_empresa.nombre_prod.nombre,
            #         #         item.piscinas,
            #         #         format(item.cantidad_egreso, '.2f'),
            #         #         format(item.producto_empresa.nombre_prod.costo, '.10f'),
            #         #         format(item.producto_empresa.nombre_prod.costo, '.10f'),
            #         #     ])
            #     # ids = Producto_Stock.objects.filter(piscinas__exact=Piscinas.objects.get(id=15), activo__exact=True).order_by('producto_empresa_id').distinct().values_list('producto_empresa_id', flat=True)
            #     # for i in Total_Stock.objects.filter(id__in=list(ids)):
            #     #     queryset = Producto_Stock.objects.filter(producto_empresa_id=i.id, fecha_ingreso__range=[start_date, end_date])
            #     #     print('----------------------------------- EL VALOR DE QUERYSET -----------------------------------')
            #     #     print(queryset)
            #     #     if queryset.exists():
            #     #         item = queryset[0]
            #     #         print('----------------------------------- EL VALOR DE ITEM -----------------------------------')
            #     #         print(queryset)
            #     #         data.append([
            #     #             item.producto_empresa.nombre_prod.nombre,
            #     #             item.piscinas,
            #     #             format(item.cantidad_egreso, '.2f'),
            #     #             format(item.producto_empresa.nombre_prod.costo, '.10f'),
            #     #             format(item.producto_empresa.nombre_prod.costo, '.10f'),
            #     #         ])
            #     dic = {}
            #     f = lambda x: x[0]
            #     for key, group in groupby(sorted(data, key=f), f):
            #         # print('Valor de Data')
            #         dic[key] = list(group)
            #     dic
            #     print(dic)
            elif action == 'search_piscina':
                data = []
                ids_excludes = json.loads(request.POST['ids'])
                queryset = Piscinas.objects.all().exclude(id__in=ids_excludes)
                for i in queryset:
                    item = i.toJSON()
                    item['dias'] = 0
                    item['siembra'] = 0
                    item['costo_larva'] = 0
                    item['dia_por_hect'] = 0
                    item['prod_cantidad_proceso'] = ''
                    item['total'] = 0
                    data.append(item)
            elif action == 'create':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    factura = PrecSiembraEnc()
                    factura.fecha_registro = request.POST['fecha_registro']
                    factura.fecha_compra = request.POST['fecha_compra']
                    factura.fecha_transferencia = request.POST['fecha_transferencia']
                    factura.observacion = request.POST['observacion']
                    factura.tot_comp = request.POST['tot_comp']
                    factura.tip_precSiembra = True
                    for fac in items:
                        factura.prod_cantidad = fac['prod_cantidad']
                        factura.resul_oper = fac['resul_oper']
                    factura.save()
                    for i in items:
                        inv = PrecSiembraCuerp()
                        inv.fecha_registro = factura
                        inv.comp_1 = request.POST['comp_1']
                        inv.comp_2 = request.POST['comp_2']
                        inv.comp_3 = request.POST['comp_3']
                        inv.tot_comp = request.POST['tot_comp']
                        producto_id = int(i['producto']) if i.get('producto') else None
                        inv.producto_id = producto_id
                        inv.prod_cantidad = i['prod_cantidad']
                        inv.piscina_id = int(i['id']) if i.get('id') else None
                        inv.dias = int(i['dias'])
                        inv.siembra = float(i['siembra']) if i.get('siembra') else 0
                        inv.costo_larva = float(i['costo_larva']) if i.get('costo_larva') else 0
                        inv.dia_por_hect = float(i['dia_por_hect']) if i.get('dia_por_hect') else 0
                        inv.prod_cantidad_proceso = i['prod_cantidad_proceso']
                        inv.total = float(i['total']) if i.get('total') else 0
                        inv.resul_oper = i['resul_oper']
                        inv.observacion = request.POST['observacion']
                        inv.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = 'el error es : ' + str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Siembra de Precrias Cuantificable'
        context['seguimiento'] = Piscinas.objects.all()
        context['piscinas'] = Piscinas.objects.all()
        context['entity'] = 'Registro de Dieta'
        context['list_url'] = self.success_url
        context['action'] = 'create'
        context['fecha_enc'] = PrecSiembraEnc.objects.all()
        context['det'] = []
        context['fec'] = ReportForm()
        return context


class listarSiembraValorizableView(ListView):
    model = PrecSiembraEnc
    template_name = 'app_corrida/app_siembra/app_siembra_cuantificable/listar_siembra.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata_val':
                data = []
                for i in PrecSiembraEnc.objects.filter(tip_precSiembra__exact = False):
                    data.append(i.toJSON())
            elif action == 'search_details_enc':
                data = []
                for i in PrecSiembraEnc.objects.filter(id=request.POST['id']):
                    data.append(i.toJSON())
            elif action == 'search_details_cuerp':
                data = []
                for i in PrecSiembraCuerp.objects.filter(fecha_registro_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Siembras Precias Cuantificable - Valorizable'
        context['title'] = 'Listado de Siembras de Precias'
        context['list_url'] = reverse_lazy('app_factura:listar_factura')
        context['entity'] = 'Siembras Precias'
        return context


class crearSiembraValorizableView(CreateView):
    model = PrecSiembraCuerp
    form_class = PrecSiembraCuerpForm
    template_name = 'app_corrida/app_siembra/app_siembra_valorizable/crear_siembra.html'
    success_url = reverse_lazy('app_dieta:principal_dia')
    url_redirect = success_url

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = []
                ids_exclude_pro = json.loads(request.POST['ids'])
                queryset_prod = Producto.objects.all().exclude(id__in=ids_exclude_pro)
                for i in queryset_prod:
                    item = i.toJSON()
                    item['prod_cantidad'] = 0
                    data.append(item)
            elif action == 'search_piscina':
                data = []
                ids_excludes = json.loads(request.POST['ids'])
                queryset = Piscinas.objects.all().exclude(id__in=ids_excludes)
                for i in queryset:
                    item = i.toJSON()
                    item['dias'] = 0
                    item['siembra'] = 0
                    item['costo_larva'] = 0
                    item['dia_por_hect'] = 0
                    item['prod_cantidad_proceso'] = ''
                    item['total'] = 0
                    data.append(item)
            elif action == 'create':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    factura = PrecSiembraEnc()
                    factura.fecha_registro = request.POST['fecha_registro']
                    factura.fecha_compra = request.POST['fecha_compra']
                    factura.fecha_transferencia = request.POST['fecha_transferencia']
                    factura.observacion = request.POST['observacion']
                    factura.tot_comp = request.POST['tot_comp']
                    factura.tip_precSiembra = False
                    for fac in items:
                        factura.prod_cantidad = fac['prod_cantidad']
                        factura.resul_oper = fac['resul_oper']
                    factura.save()
                    for i in items:
                        inv = PrecSiembraCuerp()
                        inv.fecha_registro = factura
                        inv.comp_1 = request.POST['comp_1']
                        inv.comp_2 = request.POST['comp_2']
                        inv.comp_3 = request.POST['comp_3']
                        inv.tot_comp = request.POST['tot_comp']
                        producto_id = int(i['producto']) if i.get('producto') else None
                        inv.producto_id = producto_id
                        inv.prod_cantidad = i['prod_cantidad']
                        inv.piscina_id = int(i['id']) if i.get('id') else None
                        inv.dias = int(i['dias'])
                        inv.siembra = float(i['siembra']) if i.get('siembra') else 0
                        inv.costo_larva = float(i['costo_larva']) if i.get('costo_larva') else 0
                        inv.dia_por_hect = float(i['dia_por_hect']) if i.get('dia_por_hect') else 0
                        inv.prod_cantidad_proceso = i['prod_cantidad_proceso']
                        inv.total = float(i['total']) if i.get('total') else 0
                        inv.resul_oper = i['resul_oper']
                        inv.observacion = request.POST['observacion']
                        inv.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = 'el error es : ' + str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Siembra Precrias Valorizable'
        context['seguimiento'] = Piscinas.objects.all()
        context['piscinas'] = Piscinas.objects.all()
        context['entity'] = 'Registro de Dieta'
        context['list_url'] = self.success_url
        context['action'] = 'create'
        context['fecha_enc'] = PrecSiembraEnc.objects.all()
        context['det'] = []
        return context