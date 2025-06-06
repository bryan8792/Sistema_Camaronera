import json
import os
from datetime import datetime
from io import BytesIO
import xlsxwriter
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
