import json
import os
import re
from datetime import datetime
from decimal import Decimal
from io import BytesIO
import xlsxwriter
from django.core.paginator import Paginator
from openpyxl import load_workbook
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import RequestContext, loader
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from app_contabilidad_planCuentas.forms import PlanCuentaForm, EncabezadoCuentasPlanCuentaForm, AnextoTransaccionalForm
from app_contabilidad_planCuentas.models import PlanCuenta, EncabezadoCuentasPlanCuenta, DetalleCuentasPlanCuenta, \
    AnexoTransaccional, Recibo
from app_empresa.app_reg_empresa.models import Empresa
import xml.etree.ElementTree as ET
from lxml import etree
from utilities.XML import XML
from utilities.xml_reader import XMLReader
from utilities import printer
from utilities.sri import SRI
from django.urls import reverse
import base64
import tempfile
from io import BytesIO
from django.core.files import File
import barcode

class PrintExpenseInvoiceView(View):
    success_url = reverse_lazy('app_planCuentas:listar_fact_gasto_psm')

    def get_success_url(self):
        return self.success_url

    def get(self, request, *args, **kwargs):
        print('print')
        try:
            sale = AnexoTransaccional.objects.filter(id=self.kwargs['pk']).first()
            encabezado = sale.encabezadocuentaplan
            detalle = DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan_id=sale.encabezadocuentaplan_id)
            rv = BytesIO()
            barcode.Code128(sale.access_code, writer=barcode.writer.ImageWriter()).write(rv,
                                                                                         options={'text_distance': 3.0,
                                                                                                  'font_size': 6})
            file = base64.b64encode(rv.getvalue()).decode("ascii")
            if sale:
                print('entrasss')
                print(encabezado)
                context = {'sale': sale, 'encabezado': encabezado, 'height': 450, 'detalle': detalle, 'access_code_barcode': f"data:image/png;base64,{file}"}
                pdf_file = printer.create_pdf(context=context, template_name='app_factura_gasto/format/invoice.html')
                return HttpResponse(pdf_file, content_type='application/pdf')
        except Exception as e:
            print('error')
            print(str(e))
        return HttpResponseRedirect(self.get_success_url())


class PrintExpenseInvoiceBIOView(View):
    success_url = reverse_lazy('app_planCuentas:listar_fact_gasto_bio')

    def get_success_url(self):
        return self.success_url

    def get(self, request, *args, **kwargs):
        print('print')
        try:
            sale = AnexoTransaccional.objects.filter(id=self.kwargs['pk']).first()
            encabezado = sale.encabezadocuentaplan
            detalle = DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan_id=sale.encabezadocuentaplan_id)
            rv = BytesIO()
            barcode.Code128(sale.access_code, writer=barcode.writer.ImageWriter()).write(rv,
                                                                                         options={'text_distance': 3.0,
                                                                                                  'font_size': 6})
            file = base64.b64encode(rv.getvalue()).decode("ascii")
            if sale:
                print('entrasss')
                print(encabezado)
                context = {'sale': sale, 'encabezado': encabezado, 'height': 450, 'detalle': detalle, 'access_code_barcode': f"data:image/png;base64,{file}"}
                pdf_file = printer.create_pdf(context=context, template_name='app_factura_gasto/format/invoice.html')
                return HttpResponse(pdf_file, content_type='application/pdf')
        except Exception as e:
            print('error')
            print(str(e))
        return HttpResponseRedirect(self.get_success_url())


class listarFacturaGastoPSMView(ListView):
    model = EncabezadoCuentasPlanCuenta
    template_name = 'app_factura_gasto/factura_gasto_listar.html'

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
                for i in EncabezadoCuentasPlanCuenta.objects.filter(reg_control__exact='FG', empresa__siglas__exact='PSM'):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Transacciones Empresa PSM'
        context['title'] = 'Listado de Transacciones Empresa PSM'
        context['list_url'] = reverse_lazy('app_planCuentas:listar_fact_gasto_psm')
        return context


class listarFacturaGastoBIOView(ListView):
    model = EncabezadoCuentasPlanCuenta
    template_name = 'app_factura_gasto/factura_gasto_listar_bio.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata_bio':
                data = []
                for i in EncabezadoCuentasPlanCuenta.objects.filter(reg_control__exact='FG', empresa__siglas__exact='BIO'):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Transacciones Empresa BIO'
        context['title'] = 'Listado de Transacciones Empresa BIO'
        context['list_url'] = reverse_lazy('app_planCuentas:listar_fact_gasto_bio')
        return context


class crearFacturaGastoView(CreateView):
    model = EncabezadoCuentasPlanCuenta
    form_class = EncabezadoCuentasPlanCuentaForm
    template_name = 'app_factura_gasto/factura_gasto_crear.html'
    success_url = reverse_lazy('app_planCuentas:listar_fact_gasto_psm')
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_plan':
                data = []
                empresa = request.POST['empresa']
                print('empresa de search plan')
                print(empresa)
                queryset = PlanCuenta.objects.all()
                ids_exclude = json.loads(request.POST['ids'])
                queryset = queryset.filter(empresa__siglas=empresa).exclude(id__in=ids_exclude)
                # if len(ids_exclude):
                #     queryset = queryset.filter().exclude(id__in=ids_exclude)
                for i in queryset:
                    item = i.toJSON()
                    item['detalle'] = ""
                    data.append(item)

            elif action == 'search_autocomplete':
                data = []
                ids_exclude = json.loads(request.POST['ids'])
                term = request.POST['term'].strip()
                data.append({'codigo': term, 'text': term})
                plan_detail = PlanCuenta.objects.filter(nombre__icontains=term).exclude(id__in=ids_exclude)
                for i in plan_detail[0:50]:
                    item = i.toJSON()
                    item['codigo'] = i.codigo
                    item['text'] = i.nombre
                    data.append(item)

            elif action == 'upload_xml':
                data = []
                archive = request.FILES['archive']
                factura_data = XML().read(path=archive)
                json_data = json.dumps(factura_data, ensure_ascii=False)
                data.append(json_data)
                print('json_data')
                print(json_data)

            elif action == 'search_ats':
                print('LLEGO A SEARCH ATS')
                print(request.POST)
                print("request.POST['receipt']")
                print(request.POST['receipt'])
                with transaction.atomic():
                    encabezado = EncabezadoCuentasPlanCuenta()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
                    encabezado.tip_transa = request.POST['tip_transa']
                    encabezado.fecha = request.POST['fecha']
                    encabezado.comprobante = request.POST['comprobante']
                    encabezado.descripcion = request.POST['descripcion']
                    encabezado.direccion = request.POST['direccion']
                    encabezado.reg_ats = 'CON REGISTRO DE ATS'
                    encabezado.save()
                    frmATS = AnexoTransaccional()
                    frmATS.encabezadocuentaplan_id = encabezado.pk
                    frmATS.comp_fecha_reg = request.POST['comp_fecha_reg']
                    frmATS.comp_fecha_em = request.POST['comp_fecha_em']
                    frmATS.n_autoriz = request.POST['n_autoriz']
                    frmATS.company = Empresa.objects.get(
                        siglas__exact=Empresa.objects.get(id=request.POST['company']).siglas)
                    frmATS.environment_type = frmATS.company.environment_type
                    frmATS.receipt = Recibo.objects.get(
                        voucher_type=request.POST['receipt'],
                        establishment_code=frmATS.company.establishment_code,
                        issuing_point_code=frmATS.company.issuing_point_code,
                        empresa=frmATS.company
                    )
                    frmATS.voucher_number = frmATS.generate_voucher_number()
                    frmATS.voucher_number_full = frmATS.get_voucher_number_full()
                    frmATS.save()
                    data = {
                        'print_url': str(reverse('planCuentas:factura_gasto_print_invoice', kwargs={'pk': frmATS.id}))}
                    # data = {'print_url': str(reverse('planCuentas:factura_gasto_print_invoice', kwargs={'pk': frmATS.id}))}
                    print('continuaa al generate invoice')
                    if False:  # frmATS.create_electronic_invoice:
                        data = frmATS.generate_electronic_invoice()
                        if not data['resp']:
                            print('roolback')
                            transaction.set_rollback(True)
                if 'error' in data:
                    SRI().create_voucher_errors(frmATS, data)

            elif action == 'search_voucher_number':
                try:
                    print('LLEGO A search_voucher_number')
                    print(f"Tipo de recibo recibido: {request.POST.get('receipt', '')}")
                    company_id = request.POST.get('company', None)
                    receipt_type = request.POST.get('receipt', None)
                    if not company_id:
                        data['error'] = 'Debe seleccionar una empresa válida.'
                    elif not receipt_type:
                        data['error'] = 'Debe seleccionar un tipo de recibo válido.'
                    else:
                        try:
                            company = Empresa.objects.get(id=company_id)
                            receipt = Recibo.objects.filter(
                                voucher_type=receipt_type,
                                establishment_code=company.establishment_code,
                                issuing_point_code=company.issuing_point_code,
                                empresa=company
                            ).order_by('-sequence').first()
                            if receipt:
                                data['voucher_number'] = f'{receipt.sequence + 1:09d}'
                            else:
                                data['voucher_number'] = f'{1:09d}'
                        except Empresa.DoesNotExist:
                            data['error'] = 'La empresa seleccionada no existe.'
                except Exception as e:
                    data['error'] = f'Ocurrió un error inesperado: {str(e)}'

            elif action == 'create':
                print('llego a create')
                print('request.POST')
                print(request.POST)
                # print("request.POST['empresa']")
                # print(request.POST['empresa'])
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    encabezado = EncabezadoCuentasPlanCuenta()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
                    encabezado.fecha = request.POST['fecha']
                    encabezado.ruc = request.POST['ruc']
                    encabezado.tip_transa = request.POST['tip_transa']
                    encabezado.reg_control = 'FG'
                    encabezado.empresa_id = request.POST['empresa']
                    # empresa_id = request.POST['empresa']
                    # print('empresa_id')
                    # print(empresa_id)
                    # try:
                    #     encabezado.empresa = Empresa.objects.get(pk=empresa_id)
                    # except Empresa.DoesNotExist:
                    #     return JsonResponse({'error': 'La empresa especificada no existe.'}, status=400)
                    encabezado.comprobante = request.POST['comprobante']
                    encabezado.descripcion = request.POST['descripcion']
                    encabezado.direccion = request.POST['direccion']
                    encabezado.save()
                    for i in items:
                        cuerpo = DetalleCuentasPlanCuenta()
                        cuerpo.encabezadocuentaplan_id = encabezado.pk
                        cuerpo.cuenta_id = int(i['id'])
                        cuerpo.detalle = i['detalle']
                        cuerpo.debe = int(i['debe']) if i.get('debe') else 0
                        cuerpo.haber = int(i['haber']) if i.get('haber') else 0
                        cuerpo.save()
                    data['pk'] = encabezado.pk
            else:
                print('erlo')
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = 'el error es : ' + str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Registro de Factura de Gasto'
        context['fac_gas'] = 'ES FACTURA DE GASTO'
        context['list_url'] = self.success_url
        context['action'] = 'create'
        planCuenta = PlanCuenta.objects.filter(parentId=None)
        context['planCuenta'] = planCuenta
        planCuenta2 = PlanCuenta.objects.all()
        context['planCuenta2'] = planCuenta2
        context['det'] = []
        context['existe'] = False
        context['detATS'] = []
        context['frmAnextoTransaccional'] = AnextoTransaccionalForm()
        return context


class crearFacturaGastoBIOView(CreateView):
    model = EncabezadoCuentasPlanCuenta
    form_class = EncabezadoCuentasPlanCuentaForm
    template_name = 'app_factura_gasto/factura_gasto_crear_bio.html'
    success_url = reverse_lazy('app_planCuentas:listar_fact_gasto_bio')
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            # if action == 'search_plan':
            #     data = []
            #     empresa = request.POST['empresa']
            #     print('empresa de search plan')
            #     print(empresa)
            #     queryset = PlanCuenta.objects.all()
            #     ids_exclude = json.loads(request.POST['ids'])
            #     queryset = queryset.filter(empresa__siglas=empresa).exclude(id__in=ids_exclude)
            #     # if len(ids_exclude):
            #     #     queryset = queryset.filter().exclude(id__in=ids_exclude)
            #     for i in queryset:
            #         item = i.toJSON()
            #         item['detalle'] = ""
            #         data.append(item)

            if action == 'search_plan':
                return self.search_plan_improved(request)

            # elif action == 'search_autocomplete':
            #     data = []
            #     ids_exclude = json.loads(request.POST['ids'])
            #     term = request.POST['term'].strip()
            #     data.append({'codigo': term, 'text': term})
            #     plan_detail = PlanCuenta.objects.filter(nombre__icontains=term).exclude(id__in=ids_exclude)
            #     for i in plan_detail[0:50]:
            #         item = i.toJSON()
            #         item['codigo'] = i.codigo
            #         item['text'] = i.nombre
            #         data.append(item)

            elif action == 'upload_xml':
                data = []
                archive = request.FILES['archive']
                factura_data = XML().read(path=archive)
                json_data = json.dumps(factura_data, ensure_ascii=False)
                data.append(json_data)
                print('json_data')
                print(json_data)

            elif action == 'search_recibo':
                recibos = []
                VOUCHER_TYPE = {
                    '01': 'FACTURA',
                    '04': 'NOTA DE CRÉDITO',
                    '08': 'TICKET DE VENTA',
                    '07': 'COMPROBANTE DE RETENCIÓN',
                }
                company = json.loads(request.POST['company'])
                queryset = Recibo.objects.filter(empresa_id=company)
                for r in queryset:
                    next_seq = r.sequence + 1
                    item = {
                        'codigo': r.voucher_type,  # mantén string '07' para no perder ceros
                        'text': VOUCHER_TYPE.get(r.voucher_type, r.get_voucher_type_display()),
                        'establishment_code': r.establishment_code,
                        'issuing_point_code': r.issuing_point_code,
                        'current_sequence': f'{r.sequence:09d}',  # ej. '000000006'
                        'next_sequence': f'{next_seq:09d}',  # ej. '000000007'
                        'next_sequence_raw': next_seq,  # ej. 7 (entero)
                    }
                    recibos.append(item)
                data['recibos'] = recibos

            elif action == 'search_ats':
                print('LLEGO A SEARCH ATS')
                print(request.POST)
                print("request.POST['receipt']")
                print(request.POST['receipt'])
                with transaction.atomic():
                    encabezado = EncabezadoCuentasPlanCuenta()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
                    encabezado.tip_transa = request.POST['tip_transa']
                    encabezado.fecha = request.POST['fecha']
                    encabezado.comprobante = request.POST['comprobante']
                    encabezado.descripcion = request.POST['descripcion']
                    encabezado.direccion = request.POST['direccion']
                    encabezado.reg_ats = 'CON REGISTRO DE ATS'
                    encabezado.save()
                    frmATS = AnexoTransaccional()
                    frmATS.encabezadocuentaplan_id = encabezado.pk
                    frmATS.comp_fecha_reg = request.POST['comp_fecha_reg']
                    frmATS.comp_fecha_em = request.POST['comp_fecha_em']
                    frmATS.n_autoriz = request.POST['n_autoriz']
                    frmATS.company = Empresa.objects.get(
                        siglas__exact=Empresa.objects.get(id=request.POST['company']).siglas)
                    frmATS.environment_type = frmATS.company.environment_type
                    frmATS.receipt = Recibo.objects.get(
                        voucher_type=request.POST['receipt'],
                        establishment_code=frmATS.company.establishment_code,
                        issuing_point_code=frmATS.company.issuing_point_code,
                        empresa=frmATS.company
                    )
                    frmATS.voucher_number = frmATS.generate_voucher_number()
                    frmATS.voucher_number_full = frmATS.get_voucher_number_full()
                    frmATS.save()
                    data = {
                        'print_url': str(reverse('planCuentas:factura_gasto_print_invoice', kwargs={'pk': frmATS.id}))}
                    # data = {'print_url': str(reverse('planCuentas:factura_gasto_print_invoice', kwargs={'pk': frmATS.id}))}
                    print('continuaa al generate invoice')
                    if False:  # frmATS.create_electronic_invoice:
                        data = frmATS.generate_electronic_invoice()
                        if not data['resp']:
                            print('roolback')
                            transaction.set_rollback(True)
                if 'error' in data:
                    SRI().create_voucher_errors(frmATS, data)

            elif action == 'search_voucher_number':
                try:
                    print('LLEGO A search_voucher_number')
                    print(f"Tipo de recibo recibido: {request.POST.get('receipt', '')}")
                    company_id = request.POST.get('company', None)
                    receipt_type = request.POST.get('receipt', None)
                    if not company_id:
                        data['error'] = 'Debe seleccionar una empresa válida.'
                    elif not receipt_type:
                        data['error'] = 'Debe seleccionar un tipo de recibo válido.'
                    else:
                        try:
                            company = Empresa.objects.get(id=company_id)
                            receipt = Recibo.objects.filter(
                                voucher_type=receipt_type,
                                establishment_code=company.establishment_code,
                                issuing_point_code=company.issuing_point_code,
                                empresa=company
                            ).order_by('-sequence').first()
                            if receipt:
                                data['voucher_number'] = f'{receipt.sequence + 1:09d}'
                            else:
                                data['voucher_number'] = f'{1:09d}'
                        except Empresa.DoesNotExist:
                            data['error'] = 'La empresa seleccionada no existe.'
                except Exception as e:
                    data['error'] = f'Ocurrió un error inesperado: {str(e)}'

            elif action == 'create':
                print('llego a create')
                print('request.POST')
                print(request.POST)

                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    encabezado = EncabezadoCuentasPlanCuenta()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
                    encabezado.fecha = request.POST['fecha']
                    encabezado.ruc = request.POST.get('ruc', '')  # evita MultiValueDictKeyError
                    encabezado.tip_transa = request.POST['tip_transa']
                    encabezado.reg_control = 'FG'
                    encabezado.empresa_id = request.POST['empresa']
                    encabezado.comprobante = request.POST['comprobante']
                    encabezado.descripcion = request.POST['descripcion']
                    encabezado.direccion = request.POST['direccion']
                    encabezado.save()

                    for i in items:
                        cuerpo = DetalleCuentasPlanCuenta()
                        cuerpo.encabezadocuentaplan_id = encabezado.pk
                        cuerpo.cuenta_id = int(i['id'])
                        cuerpo.detalle = i.get('detalle', '')
                        cuerpo.debe = Decimal(i.get('debe') or 0)
                        cuerpo.haber = Decimal(i.get('haber') or 0)
                        cuerpo.save()

                    data['pk'] = encabezado.pk


            # elif action == 'create':
            #     print('llego a create')
            #     print('request.POST')
            #     print(request.POST)
            #     # print("request.POST['empresa']")
            #     # print(request.POST['empresa'])
            #     with transaction.atomic():
            #         items = json.loads(request.POST['items'])
            #         encabezado = EncabezadoCuentasPlanCuenta()
            #         encabezado.codigo = request.POST['codigo']
            #         encabezado.tip_cuenta = request.POST['tip_cuenta']
            #         encabezado.fecha = request.POST['fecha']
            #         encabezado.ruc = request.POST['ruc']
            #         encabezado.tip_transa = request.POST['tip_transa']
            #         encabezado.reg_control = 'FG'
            #         encabezado.empresa_id = request.POST['empresa']
            #         # empresa_id = request.POST['empresa']
            #         # print('empresa_id')
            #         # print(empresa_id)
            #         # try:
            #         #     encabezado.empresa = Empresa.objects.get(pk=empresa_id)
            #         # except Empresa.DoesNotExist:
            #         #     return JsonResponse({'error': 'La empresa especificada no existe.'}, status=400)
            #         encabezado.comprobante = request.POST['comprobante']
            #         encabezado.descripcion = request.POST['descripcion']
            #         encabezado.direccion = request.POST['direccion']
            #         encabezado.save()
            #         for i in items:
            #             cuerpo = DetalleCuentasPlanCuenta()
            #             cuerpo.encabezadocuentaplan_id = encabezado.pk
            #             cuerpo.cuenta_id = int(i['id'])
            #             cuerpo.detalle = i['detalle']
            #             cuerpo.debe = int(i['debe']) if i.get('debe') else 0
            #             cuerpo.haber = int(i['haber']) if i.get('haber') else 0
            #             cuerpo.save()
            #         data['pk'] = encabezado.pk




            elif action == 'search_autocomplete':
                data = []
                ids_exclude = json.loads(request.POST.get('ids', '[]'))
                term = request.POST.get('term', '').strip()

                # Agregar el término de búsqueda como primera opción
                data.append({'codigo': term, 'text': term, 'id': None})

                # Buscar cuentas que coincidan con el término
                plan_detail = PlanCuenta.objects.filter(
                    Q(nombre__icontains=term) | Q(codigo__icontains=term),
                    empresa__siglas__exact='BIO'
                ).exclude(id__in=ids_exclude).order_by('codigo')[:50]

                for i in plan_detail:
                    item = i.toJSON()
                    item['codigo'] = i.codigo
                    item['text'] = f"{i.codigo} - {i.nombre}"
                    item['id'] = int(i.id) if i.id else None
                    data.append(item)

            # elif action == 'obtener_ultima_secuencia':
            #     mes = request.POST.get('mes')
            #     tipo = request.POST.get('tipo')
            #
            #     print(f"Buscando secuencia para mes={mes}, tipo={tipo}")
            #
            #     try:
            #         patron_mes = mes.lstrip('0')
            #         patron1 = f"{mes}{tipo}"
            #         patron2 = f"{patron_mes}{tipo}"
            #
            #         encabezados = EncabezadoCuentasPlanCuenta.objects.filter(
            #             Q(codigo__startswith=patron1) | Q(codigo__startswith=patron2)
            #         ).order_by('-codigo')
            #
            #         ultima_secuencia = 0
            #         if encabezados.exists():
            #             for encabezado in encabezados:
            #                 codigo = str(encabezado.codigo) if encabezado.codigo is not None else ""
            #                 print(f"Analizando código: {codigo}")
            #
            #                 match = re.search(r'(\d{1,2})(\d)(\d{3})$', codigo)
            #                 if match:
            #                     mes_encontrado = match.group(1)
            #                     tipo_encontrado = match.group(2)
            #                     secuencia_str = match.group(3)
            #
            #                     if (mes_encontrado == mes or mes_encontrado == patron_mes) and tipo_encontrado == tipo:
            #                         try:
            #                             secuencia = int(secuencia_str)
            #                             ultima_secuencia = max(ultima_secuencia, secuencia)
            #                             print(f"Secuencia encontrada: {secuencia}")
            #                         except ValueError:
            #                             print(f"Error al convertir secuencia: {secuencia_str}")
            #
            #         data['secuencia'] = ultima_secuencia
            #         print(f"Secuencia devuelta: {ultima_secuencia}")
            #
            #     except Exception as e:
            #         import traceback
            #         print(f"Error al buscar secuencia: {str(e)}")
            #         print(traceback.format_exc())
            #         data['secuencia'] = 0
            #         data['error'] = str(e)

            elif action == 'obtener_ultima_secuencia':
                mes = request.POST.get('mes')
                tipo = request.POST.get('tipo')

                print(f"Buscando secuencia para mes={mes}, tipo={tipo}")

                try:
                    # Aseguramos mes en dos dígitos
                    try:
                        mes_str = f"{int(mes):02d}"
                    except Exception:
                        mes_str = mes or "00"

                    patron_mes = mes_str.lstrip('0')
                    patron1 = f"{mes_str}{tipo}"
                    patron2 = f"{patron_mes}{tipo}"

                    encabezados = EncabezadoCuentasPlanCuenta.objects.filter(
                        Q(codigo__startswith=patron1) | Q(codigo__startswith=patron2)
                    ).order_by('-codigo')

                    ultima_secuencia = 0
                    if encabezados.exists():
                        for encabezado in encabezados:
                            codigo = str(encabezado.codigo) if encabezado.codigo else ""
                            print(f"Analizando código: {codigo}")

                            match = re.search(r'(\d{1,2})(\d)(\d{3})$', codigo)
                            if match:
                                mes_encontrado = match.group(1)
                                tipo_encontrado = match.group(2)
                                secuencia_str = match.group(3)

                                if (
                                        mes_encontrado == mes_str or mes_encontrado == patron_mes) and tipo_encontrado == str(
                                        tipo):
                                    try:
                                        secuencia = int(secuencia_str)
                                        ultima_secuencia = max(ultima_secuencia, secuencia)
                                        print(f"Secuencia encontrada: {secuencia}")
                                    except ValueError:
                                        print(f"Error al convertir secuencia: {secuencia_str}")

                    siguiente = ultima_secuencia + 1
                    next_seq_str = f"{siguiente:03d}"
                    next_codigo = f"{mes_str}{tipo}{next_seq_str}"

                    data['secuencia'] = ultima_secuencia
                    data['next_sequence'] = siguiente
                    data['next_sequence_formatted'] = next_seq_str
                    data['next_codigo'] = next_codigo

                    print(f"Última secuencia={ultima_secuencia}, siguiente={siguiente}, next_codigo={next_codigo}")

                except Exception as e:
                    import traceback
                    print(f"Error al buscar secuencia: {str(e)}")
                    print(traceback.format_exc())
                    data['secuencia'] = 0
                    data['error'] = str(e)



            else:
                print('erlo')
                data['error'] = 'Ha ocurrido un error'

        except Exception as e:
            import traceback
            print("Error en la vista:")
            print(traceback.format_exc())
            data['error'] = f'Error: {str(e)}'
        return JsonResponse(data, safe=False)


    def search_plan_improved(self, request):
        """Función mejorada para búsqueda del plan de cuentas"""
        try:
            empresa = request.POST.get('empresa', 'BIO')
            page = int(request.POST.get('page', 1))
            page_size = int(request.POST.get('page_size', 500))
            search_term = request.POST.get('search', '').strip()
            search_type = request.POST.get('search_type', 'all')  # 'all', 'exact', 'partial'
            print(f'Búsqueda: página={page}, tamaño={page_size}, término="{search_term}", tipo={search_type}')
            # Obtener IDs a excluir
            ids_exclude = []
            try:
                ids_exclude = json.loads(request.POST.get('ids', '[]'))
            except:
                ids_exclude = []
            # Construir queryset base
            queryset = PlanCuenta.objects.filter(
                empresa__siglas__exact=empresa
            ).exclude(id__in=ids_exclude)
            # Aplicar filtros de búsqueda
            if search_term:
                if search_type == 'exact':
                    # Búsqueda exacta por código
                    queryset = queryset.filter(codigo__exact=search_term)
                elif search_type == 'partial':
                    # Búsqueda parcial
                    queryset = queryset.filter(
                        Q(codigo__icontains=search_term) |
                        Q(nombre__icontains=search_term)
                    )
                else:
                    # Búsqueda general (por defecto)
                    queryset = queryset.filter(
                        Q(codigo__icontains=search_term) |
                        Q(nombre__icontains=search_term) |
                        Q(tipo_cuenta__icontains=search_term)
                    )
            # Ordenar para consistencia
            queryset = queryset.order_by('codigo', 'nombre')
            total_count = queryset.count()
            print(f'Total de registros encontrados: {total_count}')
            # Aplicar paginación
            paginator = Paginator(queryset, page_size)
            try:
                page_obj = paginator.get_page(page)
            except:
                page_obj = paginator.get_page(1)
            # Convertir a JSON
            data = []
            for item in page_obj:
                item_data = item.toJSON()
                item_data['detalle'] = ""
                data.append(item_data)
            # Respuesta con metadatos de paginación
            response_data = {
                'data': data,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_records': total_count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                    'page_size': page_size
                },
                'search_info': {
                    'term': search_term,
                    'type': search_type,
                    'found_count': total_count
                }
            }

            print(f'Enviando {len(data)} registros de {total_count} totales')
            return JsonResponse(response_data, safe=False)

        except Exception as e:
            print(f'Error en search_plan_improved: {str(e)}')
            import traceback
            print(traceback.format_exc())

            return JsonResponse({
                'error': f'Error al cargar datos: {str(e)}',
                'data': [],
                'pagination': {
                    'current_page': 1,
                    'total_pages': 0,
                    'total_records': 0,
                    'has_next': False,
                    'has_previous': False,
                    'page_size': page_size
                }
            }, status=500)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Registro de Factura de Gasto'
        context['fac_gas'] = 'ES FACTURA DE GASTO'
        context['list_url'] = self.success_url
        context['action'] = 'create'
        # Filtrar solo cuentas BIO
        planCuenta = PlanCuenta.objects.filter(parentId=None, empresa__siglas__exact='BIO')
        context['planCuenta'] = planCuenta
        planCuenta2 = PlanCuenta.objects.filter(empresa__siglas__exact='BIO')
        context['planCuenta2'] = planCuenta2
        context['empresa'] = 'BIO'
        context['det'] = []
        context['existe'] = False
        context['detATS'] = []
        context['frmAnextoTransaccional'] = AnextoTransaccionalForm()
        try:
            empresa_bio = Empresa.objects.get(siglas='BIO')
            form = self.get_form()
            form.fields['empresa'].initial = empresa_bio.id
            context['form'] = form
        except Exception as e:
            print(f"Error al preseleccionar empresa BIO: {e}")
        return context



class editarFacturaGastoView(UpdateView):
    model = EncabezadoCuentasPlanCuenta
    form_class = EncabezadoCuentasPlanCuentaForm
    template_name = 'app_factura_gasto/factura_gasto_crear.html'
    success_url = reverse_lazy('app_planCuentas:listar_fact_gasto_psm')
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_plan':
                data = []
                queryset = PlanCuenta.objects.all()
                ids_exclude = json.loads(request.POST['ids'])
                if len(ids_exclude):
                    queryset = queryset.filter().exclude(id__in=ids_exclude).order_by('codigo')
                for i in queryset.order_by('id'):
                    item = i.toJSON()
                    item['detalle'] = ""
                    data.append(item)

            elif action == 'search_autocomplete':
                data = []
                ids_exclude = json.loads(request.POST['ids'])
                term = request.POST['term'].strip()
                data.append({'codigo': term, 'text': term})
                plan_detail = PlanCuenta.objects.filter(nombre__icontains=term).exclude(id__in=ids_exclude)
                for i in plan_detail[0:50]:
                    item = i.toJSON()
                    item['codigo'] = i.codigo
                    item['text'] = i.nombre
                    data.append(item)

            elif action == 'search_recibo':
                recibos = []
                VOUCHER_TYPE = {
                    '01': 'FACTURA',
                    '04': 'NOTA DE CRÉDITO',
                    '08': 'TICKET DE VENTA',
                    '07': 'COMPROBANTE DE RETENCIÓN',
                }
                company = json.loads(request.POST['company'])
                recibo = Recibo.objects.filter(empresa_id=company)
                for i in recibo:
                    item = {}
                    item['codigo'] = i.pk
                    item['text'] = VOUCHER_TYPE[i.voucher_type]
                    recibos.append(item)
                data['recibos'] = recibos

            elif action == 'search_voucher_number':
                try:
                    print('LLEGO A search_voucher_number')
                    print(f"Tipo de recibo recibido: {request.POST.get('receipt', '')}")
                    company_id = request.POST.get('company', None)
                    receipt_type = request.POST.get('receipt', None)
                    if not company_id:
                        data['error'] = 'Debe seleccionar una empresa válida.'
                    elif not receipt_type:
                        data['error'] = 'Debe seleccionar un tipo de recibo válido.'
                    else:
                        try:
                            company = Empresa.objects.get(id=company_id)
                            receipt = Recibo.objects.filter(
                                pk=receipt_type
                            ).order_by('-sequence').first()
                            if receipt:
                                data['voucher_number'] = f'{receipt.sequence + 1:09d}'
                            else:
                                data['voucher_number'] = f'{1:09d}'
                        except Empresa.DoesNotExist:
                            data['error'] = 'La empresa seleccionada no existe.'
                except Exception as e:
                    data['error'] = f'Ocurrió un error inesperado: {str(e)}'

            elif action == 'search_ats':
                print('LLEGO A SEARCH ATS')
                print(request.POST)
                print("request.POST['receipt']")
                print(request.POST['receipt'])
                with transaction.atomic():
                    encabezado = self.get_object()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
                    encabezado.tip_transa = request.POST['tip_transa']
                    encabezado.fecha = request.POST['fecha']
                    encabezado.comprobante = request.POST['comprobante']
                    encabezado.descripcion = request.POST['descripcion']
                    encabezado.direccion = request.POST['direccion']
                    encabezado.reg_ats = 'CON REGISTRO DE ATS'
                    encabezado.save()
                    if AnexoTransaccional.objects.filter(encabezadocuentaplan_id=encabezado.pk).exists():
                        frmATS = AnexoTransaccional.objects.get(encabezadocuentaplan_id=encabezado.pk)
                    else:
                        frmATS = AnexoTransaccional()
                    frmATS.encabezadocuentaplan_id = encabezado.pk
                    frmATS.estab = request.POST['estab_serie']
                    frmATS.comp_serie = request.POST['comp_serie']
                    frmATS.comp_secuencia = request.POST['comp_secuencia']
                    frmATS.comp_numero = request.POST['comp_numero']
                    frmATS.tipo_comp = request.POST['tipo_comp']
                    frmATS.comp_fecha_reg = request.POST['comp_fecha_reg']
                    frmATS.comp_fecha_em = request.POST['comp_fecha_em']
                    frmATS.n_autoriz = request.POST['n_autoriz']
                    frmATS.ag_ret = request.POST['ag_ret']
                    frmATS.sust_trib = request.POST['sust_trib']
                    frmATS.company = Empresa.objects.get(
                        siglas__exact=Empresa.objects.get(id=request.POST['company']).siglas)
                    frmATS.environment_type = frmATS.company.environment_type
                    frmATS.cant_iva_cero = request.POST['cant_iva_cero']
                    frmATS.base_cero_bruto = request.POST['base_cero_bruto']
                    frmATS.base_cero_bruto_fcientocuatro = request.POST['base_cero_bruto_fcientocuatro']
                    frmATS.base_iva_normal_bruto_fcientocuatro = request.POST['base_iva_normal_bruto_fcientocuatro']
                    frmATS.base_iva_normal_porcen = request.POST['base_iva_normal_porcen']
                    frmATS.monto_iva_normal = request.POST['monto_iva_normal']
                    frmATS.base_iva_bienes_bruto = request.POST['base_iva_bienes_bruto']
                    frmATS.base_iva_bienes_bruto_fcientocuatro = request.POST['base_iva_bienes_bruto_fcientocuatro']
                    frmATS.base_iva_bienes_porcen = request.POST['base_iva_bienes_porcen']
                    frmATS.monto_iva_bienes = request.POST['monto_iva_bienes']
                    frmATS.base_no_obj_iva = request.POST['base_no_obj_iva']
                    frmATS.base_ice = request.POST['base_ice']
                    frmATS.porcent_ice = request.POST['porcent_ice']
                    frmATS.monto_ice = request.POST['monto_ice']
                    frmATS.monto_total = request.POST['monto_total']
                    frmATS.ret_serie = request.POST['ret_serie']
                    frmATS.ret_numero = request.POST['ret_numero']
                    frmATS.ret_numero_full = request.POST['ret_numero_full']
                    frmATS.ret_fecha = request.POST['ret_fecha']
                    frmATS.iva_cero = request.POST['iva_cero']
                    frmATS.iva_cinc = request.POST['ret_iva_cero']
                    frmATS.ret_iva_cinc = request.POST['ret_iva_cinc']
                    frmATS.cant_iva_cinc = request.POST['cant_iva_cinc']
                    frmATS.iva_diez = request.POST['iva_diez']
                    frmATS.ret_iva_diez = request.POST['ret_iva_diez']
                    frmATS.cant_iva_diez = request.POST['cant_iva_diez']
                    frmATS.iva_setn = request.POST['iva_setn']
                    frmATS.ret_iva_setn = request.POST['ret_iva_setn']
                    frmATS.cant_iva_setn = request.POST['cant_iva_setn']
                    frmATS.iva_veint = request.POST['iva_veint']
                    frmATS.ret_iva_veint = request.POST['ret_iva_veint']
                    frmATS.cant_iva_veint = request.POST['cant_iva_veint']
                    frmATS.iva_cien = request.POST['iva_cien']
                    frmATS.ret_iva_cien = request.POST['ret_iva_cien']
                    frmATS.cant_iva_cien = request.POST['cant_iva_cien']
                    frmATS.iva_treint = request.POST['iva_treint']
                    frmATS.ret_iva_treint = request.POST['ret_iva_treint']
                    frmATS.cant_iva_treint = request.POST['cant_iva_treint']
                    frmATS.ret_fue_iva_cero_uno = request.POST['ret_fue_iva_cero_uno']
                    frmATS.ret_fue_iva_uno = request.POST['ret_fue_iva_uno']
                    frmATS.ret_fue_iva_anexo_uno = request.POST['ret_fue_iva_anexo_uno']
                    frmATS.ret_fue_iva_porcent_uno = request.POST['ret_fue_iva_porcent_uno']
                    frmATS.ret_fue_iva_monto_uno = request.POST['ret_fue_iva_monto_uno']
                    frmATS.ret_fue_iva_cero_dos = request.POST['ret_fue_iva_cero_dos']
                    frmATS.ret_fue_iva_dos = request.POST['ret_fue_iva_dos']
                    frmATS.ret_fue_iva_anexo_dos = request.POST['ret_fue_iva_anexo_dos']
                    frmATS.ret_fue_iva_porcent_dos = request.POST['ret_fue_iva_porcent_dos']
                    frmATS.ret_fue_iva_monto_dos = request.POST['ret_fue_iva_monto_dos']
                    frmATS.ret_fue_iva_cero_tres = request.POST['ret_fue_iva_cero_tres']
                    frmATS.ret_fue_iva_tres = request.POST['ret_fue_iva_tres']
                    frmATS.ret_fue_iva_anexo_tres = request.POST['ret_fue_iva_anexo_tres']
                    frmATS.ret_fue_iva_porcent_tres = request.POST['ret_fue_iva_porcent_tres']
                    frmATS.ret_fue_iva_monto_tres = request.POST['ret_fue_iva_monto_tres']
                    # frmATS.tip_form = request.POST['tip_form']
                    # frmATS.det_form = request.POST['det_form']
                    print('frmATS.company.establishment_code')
                    print(frmATS.company.establishment_code)
                    print('frmATS.company.issuing_point_code')
                    print(frmATS.company.issuing_point_code)
                    print('frmATS.company')
                    print(frmATS.company_id)
                    recibo = Recibo.objects.get(
                        pk=request.POST['receipt']
                    )
                    frmATS.receipt = recibo
                    print('continua')
                    frmATS.voucher_number = frmATS.generate_voucher_number()
                    frmATS.voucher_number_full = frmATS.get_voucher_number_full()
                    frmATS.save()
                    recibo.sequence = recibo.sequence + 1
                    recibo.save()
                    data = {
                        'print_url': str(reverse('planCuentas:factura_gasto_print_invoice', kwargs={'pk': frmATS.id}))}
                    # data = {'print_url': str(reverse('planCuentas:factura_gasto_print_invoice', kwargs={'pk': frmATS.id}))}
                    print('continuaa al generate invoice')
                    if frmATS.create_electronic_invoice:
                        data = frmATS.generate_electronic_invoice()
                        if not data['resp']:
                            print('roolback')
                            transaction.set_rollback(True)
                if 'error' in data:
                    SRI().create_voucher_errors(frmATS, data)

            elif action == 'edit':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    encabezado = self.get_object()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
                    encabezado.tip_transa = request.POST['tip_transa']
                    encabezado.fecha = request.POST['fecha']
                    encabezado.comprobante = request.POST['comprobante']
                    encabezado.descripcion = request.POST['descripcion']
                    encabezado.direccion = request.POST['direccion']
                    encabezado.save()
                    for s in encabezado.detallecuentasplancuenta_set.all():
                        print('s del recorredor')
                        print(s)
                    # encabezado.detallecuentasplancuenta_set.all().delete()
                    for i in items:
                        cuerpo = DetalleCuentasPlanCuenta()
                        cuerpo.encabezadocuentaplan_id = encabezado.pk
                        cuerpo.cuenta_id = int(i['id'])
                        cuerpo.detalle = i['detalle']
                        cuerpo.debe = int(i['debe']) if i.get('debe') else 0
                        cuerpo.haber = int(i['haber']) if i.get('haber') else 0
                        cuerpo.save()
            else:
                print('ol')
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = 'el error es : ' + str(e)
        return JsonResponse(data, safe=False)

    def get_detalle(self):
        data = []
        for i in DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan_id=self.kwargs['pk']):
            item = i.cuenta.toJSON()
            item['detalle'] = i.detalle
            item['debe'] = format(i.debe, '.2f')
            item['haber'] = format(i.haber, '.2f')
            data.append(item)
        return json.dumps(data)

    def get_detail_anexo(self):
        data = []
        try:
            for i in AnexoTransaccional.objects.filter(detallecuentaplan_id=self.get_object().id):
                item = i.toJSON()
                data.append(item)
            return json.dumps(data)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Formulario de Edición de Factura de Gasto'
        context['fac_gas'] = 'ES FACTURA DE GASTO'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        planCuenta = PlanCuenta.objects.filter(parentId=None)
        context['planCuenta'] = planCuenta
        planCuenta2 = PlanCuenta.objects.all()
        context['planCuenta2'] = planCuenta2
        context['existe'] = True
        context['det'] = self.get_detalle()
        context['detATS'] = self.get_detail_anexo()
        context['frmAnextoTransaccional'] = AnextoTransaccionalForm()
        if AnexoTransaccional.objects.filter(encabezadocuentaplan_id=self.get_object().id).exists():
            transa = AnexoTransaccional.objects.get(encabezadocuentaplan_id=self.get_object().id)
            context['frmAnextoTransaccional'] = AnextoTransaccionalForm(instance=transa)
        else:
            context['frmAnextoTransaccional'] = AnextoTransaccionalForm()
        return context


class editarFacturaGastoBIOView(UpdateView):
    model = EncabezadoCuentasPlanCuenta
    form_class = EncabezadoCuentasPlanCuentaForm
    template_name = 'app_factura_gasto/factura_gasto_crear_bio.html'
    success_url = reverse_lazy('app_planCuentas:listar_fact_gasto_bio')
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            # if action == 'search_plan':
            #     data = []
            #     queryset = PlanCuenta.objects.all()
            #     ids_exclude = json.loads(request.POST['ids'])
            #     if len(ids_exclude):
            #         queryset = queryset.filter().exclude(id__in=ids_exclude).order_by('codigo')
            #     for i in queryset.order_by('id'):
            #         item = i.toJSON()
            #         item['detalle'] = ""
            #         data.append(item)

            if action == 'search_plan':
                return self.search_plan_improved(request)

            elif action == 'search_autocomplete':
                data = []
                ids_exclude = json.loads(request.POST['ids'])
                term = request.POST['term'].strip()
                data.append({'codigo': term, 'text': term})
                plan_detail = PlanCuenta.objects.filter(nombre__icontains=term).exclude(id__in=ids_exclude)
                for i in plan_detail[0:50]:
                    item = i.toJSON()
                    item['codigo'] = i.codigo
                    item['text'] = i.nombre
                    data.append(item)

            elif action == 'upload_xml':
                data = []
                archive = request.FILES['archive']
                factura_data = XML().read(path=archive)
                json_data = json.dumps(factura_data, ensure_ascii=False)
                data.append(json_data)
                print('json_data')
                print(json_data)

            elif action == 'search_recibo':
                recibos = []
                VOUCHER_TYPE = {
                    '01': 'FACTURA',
                    '04': 'NOTA DE CRÉDITO',
                    '08': 'TICKET DE VENTA',
                    '07': 'COMPROBANTE DE RETENCIÓN',
                }
                company = json.loads(request.POST['company'])
                recibo = Recibo.objects.filter(empresa_id=company)
                for i in recibo:
                    item = {}
                    item['codigo'] = i.pk
                    item['text'] = VOUCHER_TYPE[i.voucher_type]
                    recibos.append(item)
                data['recibos'] = recibos

            # elif action == 'search_voucher_number':
            #     try:
            #         print('LLEGO A search_voucher_number')
            #         print(f"Tipo de recibo recibido: {request.POST.get('receipt', '')}")
            #         company_id = request.POST.get('company', None)
            #         receipt_type = request.POST.get('receipt', None)
            #         if not company_id:
            #             data['error'] = 'Debe seleccionar una empresa válida.'
            #         elif not receipt_type:
            #             data['error'] = 'Debe seleccionar un tipo de recibo válido.'
            #         else:
            #             try:
            #                 company = Empresa.objects.get(id=company_id)
            #                 receipt = Recibo.objects.filter(
            #                     pk=receipt_type
            #                 ).order_by('-sequence').first()
            #                 if receipt:
            #                     data['voucher_number'] = f'{receipt.sequence + 1:09d}'
            #                 else:
            #                     data['voucher_number'] = f'{1:09d}'
            #             except Empresa.DoesNotExist:
            #                 data['error'] = 'La empresa seleccionada no existe.'
            #     except Exception as e:
            #         data['error'] = f'Ocurrió un error inesperado: {str(e)}'

            elif action == 'search_voucher_number':
                try:
                    print('LLEGO A search_voucher_number')
                    print(f"Tipo de recibo recibido: {request.POST.get('receipt', '')}")
                    company_id = request.POST.get('company', None)
                    receipt_type = request.POST.get('receipt', None)
                    if not company_id:
                        data['error'] = 'Debe seleccionar una empresa válida.'
                    elif not receipt_type:
                        data['error'] = 'Debe seleccionar un tipo de recibo válido.'
                    else:
                        try:
                            company = Empresa.objects.get(id=company_id)
                            receipt = Recibo.objects.filter(
                                voucher_type=receipt_type,
                                establishment_code=company.establishment_code,
                                issuing_point_code=company.issuing_point_code,
                                empresa=company
                            ).order_by('-sequence').first()
                            if receipt:
                                data['voucher_number'] = f'{receipt.sequence + 1:09d}'
                            else:
                                data['voucher_number'] = f'{1:09d}'
                        except Empresa.DoesNotExist:
                            data['error'] = 'La empresa seleccionada no existe.'
                except Exception as e:
                    data['error'] = f'Ocurrió un error inesperado: {str(e)}'

            elif action == 'search_ats':
                print('LLEGO A SEARCH ATS')
                print(request.POST)
                print("request.POST['receipt']")
                print(request.POST['receipt'])
                with transaction.atomic():
                    encabezado = self.get_object()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
                    encabezado.fecha = request.POST['fecha']
                    encabezado.ruc = request.POST.get('ruc', '')
                    encabezado.tip_transa = request.POST['tip_transa']
                    encabezado.reg_control = 'FG'
                    encabezado.empresa_id = request.POST['empresa']
                    encabezado.comprobante = request.POST['comprobante']
                    encabezado.descripcion = request.POST['descripcion']
                    encabezado.direccion = request.POST['direccion']
                    encabezado.reg_ats = 'CON REGISTRO DE ATS'
                    encabezado.save()
                    if AnexoTransaccional.objects.filter(encabezadocuentaplan_id=encabezado.pk).exists():
                        frmATS = AnexoTransaccional.objects.get(encabezadocuentaplan_id=encabezado.pk)
                    else:
                        frmATS = AnexoTransaccional()
                    frmATS.encabezadocuentaplan_id = encabezado.pk
                    frmATS.estab = request.POST['estab_serie']
                    frmATS.comp_serie = request.POST['comp_serie']
                    frmATS.comp_secuencia = request.POST['comp_secuencia']
                    frmATS.comp_numero = request.POST['comp_numero']
                    frmATS.tipo_comp = request.POST['tipo_comp']
                    frmATS.comp_fecha_reg = request.POST['comp_fecha_reg']
                    frmATS.comp_fecha_em = request.POST['comp_fecha_em']
                    frmATS.n_autoriz = request.POST['n_autoriz']
                    frmATS.ag_ret = request.POST['ag_ret']
                    frmATS.sust_trib = request.POST['sust_trib']
                    frmATS.company = Empresa.objects.get(
                        siglas__exact=Empresa.objects.get(id=request.POST['company']).siglas)
                    frmATS.environment_type = frmATS.company.environment_type
                    frmATS.cant_iva_cero = request.POST['cant_iva_cero']
                    frmATS.base_cero_bruto = request.POST['base_cero_bruto']
                    frmATS.base_cero_bruto_fcientocuatro = request.POST['base_cero_bruto_fcientocuatro']
                    frmATS.base_iva_normal_bruto_fcientocuatro = request.POST['base_iva_normal_bruto_fcientocuatro']
                    frmATS.base_iva_normal_porcen = request.POST['base_iva_normal_porcen']
                    frmATS.monto_iva_normal = request.POST['monto_iva_normal']
                    frmATS.base_iva_bienes_bruto = request.POST['base_iva_bienes_bruto']
                    frmATS.base_iva_bienes_bruto_fcientocuatro = request.POST['base_iva_bienes_bruto_fcientocuatro']
                    frmATS.base_iva_bienes_porcen = request.POST['base_iva_bienes_porcen']
                    frmATS.monto_iva_bienes = request.POST['monto_iva_bienes']
                    frmATS.base_no_obj_iva = request.POST['base_no_obj_iva']
                    frmATS.base_ice = request.POST['base_ice']
                    frmATS.porcent_ice = request.POST['porcent_ice']
                    frmATS.monto_ice = request.POST['monto_ice']
                    frmATS.monto_total = request.POST['monto_total']
                    frmATS.ret_serie = request.POST['ret_serie']
                    frmATS.ret_numero = request.POST['ret_numero']
                    frmATS.ret_numero_full = request.POST['ret_numero_full']
                    frmATS.ret_fecha = request.POST['ret_fecha']
                    frmATS.iva_cero = request.POST['iva_cero']
                    frmATS.iva_cinc = request.POST['ret_iva_cero']
                    frmATS.ret_iva_cinc = request.POST['ret_iva_cinc']
                    frmATS.cant_iva_cinc = request.POST['cant_iva_cinc']
                    frmATS.iva_diez = request.POST['iva_diez']
                    frmATS.ret_iva_diez = request.POST['ret_iva_diez']
                    frmATS.cant_iva_diez = request.POST['cant_iva_diez']
                    frmATS.iva_setn = request.POST['iva_setn']
                    frmATS.ret_iva_setn = request.POST['ret_iva_setn']
                    frmATS.cant_iva_setn = request.POST['cant_iva_setn']
                    frmATS.iva_veint = request.POST['iva_veint']
                    frmATS.ret_iva_veint = request.POST['ret_iva_veint']
                    frmATS.cant_iva_veint = request.POST['cant_iva_veint']
                    frmATS.iva_cien = request.POST['iva_cien']
                    frmATS.ret_iva_cien = request.POST['ret_iva_cien']
                    frmATS.cant_iva_cien = request.POST['cant_iva_cien']
                    frmATS.iva_treint = request.POST['iva_treint']
                    frmATS.ret_iva_treint = request.POST['ret_iva_treint']
                    frmATS.cant_iva_treint = request.POST['cant_iva_treint']
                    frmATS.ret_fue_iva_cero_uno = request.POST['ret_fue_iva_cero_uno']
                    frmATS.ret_fue_iva_uno = request.POST['ret_fue_iva_uno']
                    frmATS.ret_fue_iva_anexo_uno = request.POST['ret_fue_iva_anexo_uno']
                    frmATS.ret_fue_iva_porcent_uno = request.POST['ret_fue_iva_porcent_uno']
                    frmATS.ret_fue_iva_monto_uno = request.POST['ret_fue_iva_monto_uno']
                    frmATS.ret_fue_iva_cero_dos = request.POST['ret_fue_iva_cero_dos']
                    frmATS.ret_fue_iva_dos = request.POST['ret_fue_iva_dos']
                    frmATS.ret_fue_iva_anexo_dos = request.POST['ret_fue_iva_anexo_dos']
                    frmATS.ret_fue_iva_porcent_dos = request.POST['ret_fue_iva_porcent_dos']
                    frmATS.ret_fue_iva_monto_dos = request.POST['ret_fue_iva_monto_dos']
                    frmATS.ret_fue_iva_cero_tres = request.POST['ret_fue_iva_cero_tres']
                    frmATS.ret_fue_iva_tres = request.POST['ret_fue_iva_tres']
                    frmATS.ret_fue_iva_anexo_tres = request.POST['ret_fue_iva_anexo_tres']
                    frmATS.ret_fue_iva_porcent_tres = request.POST['ret_fue_iva_porcent_tres']
                    frmATS.ret_fue_iva_monto_tres = request.POST['ret_fue_iva_monto_tres']
                    # frmATS.tip_form = request.POST['tip_form']
                    # frmATS.det_form = request.POST['det_form']
                    print('frmATS.company.establishment_code')
                    print(frmATS.company.establishment_code)
                    print('frmATS.company.issuing_point_code')
                    print(frmATS.company.issuing_point_code)
                    print('frmATS.company')
                    print(frmATS.company_id)
                    recibo = Recibo.objects.get(
                        pk=request.POST['receipt']
                    )
                    frmATS.receipt = recibo
                    print('continua')
                    frmATS.voucher_number = frmATS.generate_voucher_number()
                    frmATS.voucher_number_full = frmATS.get_voucher_number_full()
                    frmATS.save()
                    recibo.sequence = recibo.sequence + 1
                    recibo.save()
                    data = {
                        'print_url': str(reverse('planCuentas:factura_gasto_bio_print_invoice', kwargs={'pk': frmATS.id}))}
                    # data = {'print_url': str(reverse('planCuentas:factura_gasto_print_invoice', kwargs={'pk': frmATS.id}))}
                    print('continuaa al generate invoice')
                    if frmATS.create_electronic_invoice:
                        data = frmATS.generate_electronic_invoice()
                        if not data['resp']:
                            print('roolback')
                            transaction.set_rollback(True)
                if 'error' in data:
                    SRI().create_voucher_errors(frmATS, data)

            elif action == 'edit':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    encabezado = self.get_object()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
                    encabezado.tip_transa = request.POST['tip_transa']
                    encabezado.fecha = request.POST['fecha']
                    encabezado.ruc = request.POST.get('ruc', '')
                    encabezado.comprobante = request.POST['comprobante']
                    encabezado.descripcion = request.POST['descripcion']
                    encabezado.direccion = request.POST['direccion']
                    encabezado.save()
                    for s in encabezado.detallecuentasplancuenta_set.all():
                        print('s del recorredor')
                        print(s)
                    # encabezado.detallecuentasplancuenta_set.all().delete()
                    for i in items:
                        cuerpo = DetalleCuentasPlanCuenta()
                        cuerpo.encabezadocuentaplan_id = encabezado.pk
                        cuerpo.cuenta_id = int(i['id'])
                        cuerpo.detalle = i['detalle']
                        cuerpo.debe = int(i['debe']) if i.get('debe') else 0
                        cuerpo.haber = int(i['haber']) if i.get('haber') else 0
                        cuerpo.save()
            else:
                print('ol')
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = 'el error es : ' + str(e)
        return JsonResponse(data, safe=False)

    def get_detalle(self):
        data = []
        for i in DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan_id=self.kwargs['pk']):
            item = i.cuenta.toJSON()
            item['detalle'] = i.detalle
            item['debe'] = format(i.debe, '.2f')
            item['haber'] = format(i.haber, '.2f')
            data.append(item)
        return json.dumps(data)

    def get_detail_anexo(self):
        data = []
        try:
            for i in AnexoTransaccional.objects.filter(detallecuentaplan_id=self.get_object().id):
                item = i.toJSON()
                data.append(item)
            return json.dumps(data)
        except:
            pass
        return data

    def search_plan_improved(self, request):
        """Función mejorada para búsqueda del plan de cuentas"""
        try:
            empresa = request.POST.get('empresa', 'BIO')
            page = int(request.POST.get('page', 1))
            page_size = int(request.POST.get('page_size', 500))
            search_term = request.POST.get('search', '').strip()
            search_type = request.POST.get('search_type', 'all')  # 'all', 'exact', 'partial'
            print(f'Búsqueda: página={page}, tamaño={page_size}, término="{search_term}", tipo={search_type}')
            # Obtener IDs a excluir
            ids_exclude = []
            try:
                ids_exclude = json.loads(request.POST.get('ids', '[]'))
            except:
                ids_exclude = []
            # Construir queryset base
            queryset = PlanCuenta.objects.filter(
                empresa__siglas__exact=empresa
            ).exclude(id__in=ids_exclude)
            # Aplicar filtros de búsqueda
            if search_term:
                if search_type == 'exact':
                    # Búsqueda exacta por código
                    queryset = queryset.filter(codigo__exact=search_term)
                elif search_type == 'partial':
                    # Búsqueda parcial
                    queryset = queryset.filter(
                        Q(codigo__icontains=search_term) |
                        Q(nombre__icontains=search_term)
                    )
                else:
                    # Búsqueda general (por defecto)
                    queryset = queryset.filter(
                        Q(codigo__icontains=search_term) |
                        Q(nombre__icontains=search_term) |
                        Q(tipo_cuenta__icontains=search_term)
                    )
            # Ordenar para consistencia
            queryset = queryset.order_by('codigo', 'nombre')
            total_count = queryset.count()
            print(f'Total de registros encontrados: {total_count}')
            # Aplicar paginación
            paginator = Paginator(queryset, page_size)
            try:
                page_obj = paginator.get_page(page)
            except:
                page_obj = paginator.get_page(1)
            # Convertir a JSON
            data = []
            for item in page_obj:
                item_data = item.toJSON()
                item_data['detalle'] = ""
                data.append(item_data)
            # Respuesta con metadatos de paginación
            response_data = {
                'data': data,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_records': total_count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                    'page_size': page_size
                },
                'search_info': {
                    'term': search_term,
                    'type': search_type,
                    'found_count': total_count
                }
            }

            print(f'Enviando {len(data)} registros de {total_count} totales')
            return JsonResponse(response_data, safe=False)

        except Exception as e:
            print(f'Error en search_plan_improved: {str(e)}')
            import traceback
            print(traceback.format_exc())

            return JsonResponse({
                'error': f'Error al cargar datos: {str(e)}',
                'data': [],
                'pagination': {
                    'current_page': 1,
                    'total_pages': 0,
                    'total_records': 0,
                    'has_next': False,
                    'has_previous': False,
                    'page_size': page_size
                }
            }, status=500)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Formulario de Edición de Factura de Gasto'
        context['fac_gas'] = 'ES FACTURA DE GASTO'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        planCuenta = PlanCuenta.objects.filter(parentId=None)
        context['planCuenta'] = planCuenta
        planCuenta2 = PlanCuenta.objects.all()
        context['planCuenta2'] = planCuenta2
        context['existe'] = True
        context['det'] = self.get_detalle()
        context['detATS'] = self.get_detail_anexo()
        context['frmAnextoTransaccional'] = AnextoTransaccionalForm()
        if AnexoTransaccional.objects.filter(encabezadocuentaplan_id=self.get_object().id).exists():
            transa = AnexoTransaccional.objects.get(encabezadocuentaplan_id=self.get_object().id)
            context['frmAnextoTransaccional'] = AnextoTransaccionalForm(instance=transa)
        else:
            context['frmAnextoTransaccional'] = AnextoTransaccionalForm()
        return context


#
# class eliminarTransaccionPlanView(DeleteView):
#     model = InvoiceStock
#     template_name = 'app_factura_detalle/factura_detalle_eliminar.html'
#     success_url = reverse_lazy('app_factura:listar_factura')
#     url_redirect = success_url
#
#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             self.object.delete()
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Eliminación de una Factura'
#         context['entity'] = 'Factura'
#         context['list_url'] = reverse_lazy('app_factura:listar_factura')
#         return context
