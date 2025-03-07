
import json
import os
from datetime import datetime
from io import BytesIO
import xlsxwriter
from openpyxl import load_workbook
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import RequestContext, loader
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from app_contabilidad_planCuentas.forms import PlanCuentaForm, EncabezadoCuentasPlanCuentaForm
from app_contabilidad_planCuentas.models import PlanCuenta, Folder, EncabezadoCuentasPlanCuenta, DetalleCuentasPlanCuenta
from app_empresa.app_reg_empresa.models import Empresa
from collections import defaultdict
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum, F, Q
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def _inicializar():
    Folder.objects.all().delete()
    folder_raiz = Folder(
        name='Plan de Cuentas'
    )
    folder_raiz.save()
    folder_raiz2 = Folder(
        name='Plan de Cuentas V2'
    )
    folder_raiz2.save()
    folder = Folder(
        name='Docs',
        parent=folder_raiz
    )
    folder.save()
    folder_trab = Folder(
        name='Trabajo',
        parent=folder
    )
    folder_trab.save()

    folder = Folder(
        name='Música',
        parent=folder_raiz
    )
    folder.save()
    folder_photos = Folder(
        name='Fotos',
        parent=folder_raiz
    )
    folder_photos.save()
    folder = Folder(
        name='Vacaciones',
        parent=folder_photos
    )
    folder.save()
    folder = Folder(
        name='Trabajo',
        parent=folder_photos
    )
    folder.save()


# CREAR PLAN DE CUENTAS
class crearPlanCuentaView(CreateView):
    model = PlanCuenta
    form_class = PlanCuentaForm
    template_name = 'app_contabilidad_planCuentas/parts_Plan/planCuenta_crear.html'
    success_url = reverse_lazy('app_planCuentas:listar_planCuenta_BIO')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Formulario de Registro de Plan de Cuenta'
        context['action'] = 'add'
        context['list_url'] = self.success_url
        return context

# ACTUALIZAR PLAN DE CUENTAS
class actualizarPlanCuentaView(UpdateView):
    model = PlanCuenta
    form_class = PlanCuentaForm
    template_name = 'app_contabilidad_planCuentas/parts_Plan/planCuenta_crear.html'
    success_url = reverse_lazy('app_planCuentas:listar_planCuenta_BIO')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Plan de Cuenta'
        context['action'] = 'edit'
        context['list_url'] = self.success_url
        return context

# ELIMINAR PLAN DE CUENTAS
class eliminarPlanCuentaView(DeleteView):
    model = PlanCuenta
    form_class = PlanCuentaForm
    template_name = 'app_contabilidad_planCuentas/parts_Plan/planCuenta_eliminar.html'
    success_url = reverse_lazy('app_planCuentas:listar_planCuenta_BIO')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Plan de Cuenta'
        context['list_url'] = self.success_url
        return context

# LISTAR PLAN DE CUENTAS
class listarPlanCuentaBIOView(TemplateView):
    model = PlanCuenta
    template_name = 'app_contabilidad_planCuentas/parts_Plan/foldersBIO.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # _inicializar()
        return super().dispatch(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     data = {}
    #     try:
    #         data = PlanCuenta.objects.get(pk=request.POST['id']).toJSON()
    #         print('data')
    #         print(data)
    #     except Exception as e:
    #         data['error'] = str(e)
    #     return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'searchdataBIO':
                data = []
                empresa = request.POST['empresa']
                queryset = PlanCuenta.objects.all()
                queryset = queryset.filter(empresa__siglas=empresa).order_by('codigo')
                for i in queryset:
                    data.append(i.toJSON())

            elif action == 'upload_excel':
                print('llego a Upload excell empezo a recorrer en el python desde ajax')
                with transaction.atomic():
                    archive = request.FILES['archive']
                    workbook = load_workbook(filename=archive, data_only=True)
                    excel = workbook[workbook.sheetnames[0]]

                    for row in range(2, excel.max_row + 1):
                        name_empresa = excel.cell(row=row, column=7).value

                        # Validar si la empresa existe por sus siglas
                        empresa, created = Empresa.objects.get_or_create(
                            siglas=name_empresa,
                            defaults={
                                'nombre': name_empresa  # Ajustar según sea necesario si las siglas son distintas
                            }
                        )

                        print(f"{'Nueva empresa creada' if created else 'Empresa existente'}: {empresa.nombre} con siglas {empresa.siglas}")

                        # Buscar o inicializar la cuenta contable
                        codigo_cuenta = excel.cell(row=row, column=2).value
                        product, created = PlanCuenta.objects.get_or_create(
                            empresa=empresa,
                            codigo=codigo_cuenta,
                            defaults={
                                'nombre': excel.cell(row=row, column=3).value,
                                'nivel': int(excel.cell(row=row, column=4).value),
                                'tipo_cuenta': excel.cell(row=row, column=5).value,
                                'periodo': int(excel.cell(row=row, column=8).value)
                            }
                        )

                        # Si la cuenta ya existe, actualizarla con los nuevos valores
                        if not created:
                            product.nombre = excel.cell(row=row, column=3).value
                            product.nivel = int(excel.cell(row=row, column=4).value)
                            product.tipo_cuenta = excel.cell(row=row, column=5).value
                            product.periodo = int(excel.cell(row=row, column=8).value)

                        # Manejo del padre (cuenta superior)
                        codigo_padre = excel.cell(row=row, column=6).value
                        if codigo_padre:
                            try:
                                padre = PlanCuenta.objects.get(codigo=codigo_padre, empresa=empresa)
                                product.parentId = padre
                            except PlanCuenta.DoesNotExist:
                                # Si no existe el padre, mostrar un mensaje o manejar el error
                                print(f"Cuenta padre con código {codigo_padre} no existe para la empresa {empresa.siglas}")

                        product.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Listado de Plan de Cuentas'
        planCuenta = PlanCuenta.objects.filter(parentId=None)
        context['planCuenta'] = planCuenta
        folders = Folder.objects.filter(parent=None)
        context['folders'] = folders
        return context

# PLAN DE CUENTAS DE LA EMPRESA PSM CREAR
class crearPlanCuentaPSMView(CreateView):
    model = PlanCuenta
    form_class = PlanCuentaForm
    template_name = 'app_contabilidad_planCuentas/parts_Plan/planCuenta_crear_psm.html'
    success_url = reverse_lazy('app_planCuentas:listar_planCuenta_PSM')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Formulario de Registro de Plan de Cuenta'
        context['action'] = 'add'
        context['list_url'] = self.success_url
        return context

# ACTUALIZAR PLAN DE CUENTAS
class actualizarPlanCuentaPSMView(UpdateView):
    model = PlanCuenta
    form_class = PlanCuentaForm
    template_name = 'app_contabilidad_planCuentas/parts_Plan/planCuenta_crear_psm.html'
    success_url = reverse_lazy('app_planCuentas:listar_planCuenta_PSM')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Plan de Cuenta'
        context['action'] = 'edit'
        context['list_url'] = self.success_url
        return context

# ELIMINAR PLAN DE CUENTAS
class eliminarPlanCuentaPSMView(DeleteView):
    model = PlanCuenta
    form_class = PlanCuentaForm
    template_name = 'app_contabilidad_planCuentas/parts_Plan/planCuenta_crear_psm.html'
    success_url = reverse_lazy('app_planCuentas:listar_planCuenta_PSM')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Plan de Cuenta'
        context['list_url'] = self.success_url
        return context

#     LISTAR PLAN DE CUENTAS PSM
class listarPlanCuentaPSMView(TemplateView):
    model = PlanCuenta
    template_name = 'app_contabilidad_planCuentas/parts_Plan/foldersPSM.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # _inicializar()
        return super().dispatch(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     data = {}
    #     try:
    #         data = PlanCuenta.objects.get(pk=request.POST['id']).toJSON()
    #         print('data')
    #         print(data)
    #     except Exception as e:
    #         data['error'] = str(e)
    #     return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'searchdataPSM':
                data = []
                empresa = request.POST['empresa']
                queryset = PlanCuenta.objects.all()
                queryset = queryset.filter(empresa__siglas=empresa).order_by('codigo')
                for i in queryset:
                    data.append(i.toJSON())

            elif action == 'upload_excel':
                print('llego a Upload excell empezo a recorrer en el python desde ajax')
                with transaction.atomic():
                    archive = request.FILES['archive']
                    workbook = load_workbook(filename=archive, data_only=True)
                    excel = workbook[workbook.sheetnames[0]]

                    for row in range(2, excel.max_row + 1):
                        name_empresa = excel.cell(row=row, column=7).value

                        # Validar si la empresa existe por sus siglas
                        empresa, created = Empresa.objects.get_or_create(
                            siglas=name_empresa,
                            defaults={
                                'nombre': name_empresa  # Ajustar según sea necesario si las siglas son distintas
                            }
                        )

                        print(f"{'Nueva empresa creada' if created else 'Empresa existente'}: {empresa.nombre} con siglas {empresa.siglas}")

                        # Buscar o inicializar la cuenta contable
                        codigo_cuenta = excel.cell(row=row, column=2).value
                        product, created = PlanCuenta.objects.get_or_create(
                            empresa=empresa,
                            codigo=codigo_cuenta,
                            defaults={
                                'nombre': excel.cell(row=row, column=3).value,
                                'nivel': int(excel.cell(row=row, column=4).value),
                                'tipo_cuenta': excel.cell(row=row, column=5).value,
                                'periodo': int(excel.cell(row=row, column=8).value)
                            }
                        )

                        # Si la cuenta ya existe, actualizarla con los nuevos valores
                        if not created:
                            product.nombre = excel.cell(row=row, column=3).value
                            product.nivel = int(excel.cell(row=row, column=4).value)
                            product.tipo_cuenta = excel.cell(row=row, column=5).value
                            product.periodo = int(excel.cell(row=row, column=8).value)

                        # Manejo del padre (cuenta superior)
                        codigo_padre = excel.cell(row=row, column=6).value
                        if codigo_padre:
                            try:
                                padre = PlanCuenta.objects.get(codigo=codigo_padre, empresa=empresa)
                                product.parentId = padre
                            except PlanCuenta.DoesNotExist:
                                # Si no existe el padre, mostrar un mensaje o manejar el error
                                print(f"Cuenta padre con código {codigo_padre} no existe para la empresa {empresa.siglas}")

                        product.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Listado de Plan de Cuentas'
        planCuenta = PlanCuenta.objects.filter(parentId=None)
        context['planCuenta'] = planCuenta
        folders = Folder.objects.filter(parent=None)
        context['folders'] = folders
        return context


# EXPORTAR A EXCELL PLAN DE CUENTAS
class PlanExportExcelBIOView(View):
    def get(self, request, *args, **kwargs):
        try:
            headers = {
                'id': 10,
                'CODIGO': 15,
                'NOMBRE': 75,
                'NIVEL': 20,
                'GEN_DET': 20,
                'CTA_MAY': 20,
                'EMPRESA': 20,
                'PERIODO': 20,
            }

            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('plan_cuentas')
            cell_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
            row_format = workbook.add_format({'align': 'center', 'border': 1})
            row_format2 = workbook.add_format({'align': 'left', 'border': 1})
            index = 0
            for name, width in headers.items():
                worksheet.set_column(first_col=0, last_col=index, width=width)
                worksheet.write(0, index, name, cell_format)
                index += 1
            row = 1
            queryset = PlanCuenta.objects.all()
            queryset = queryset.filter(empresa__siglas='BIO').order_by('id')
            for product in queryset:
                worksheet.write(row, 0, product.id, row_format)
                worksheet.write(row, 1, product.codigo, row_format2)
                worksheet.write(row, 2, product.nombre, row_format2)
                worksheet.write(row, 3, product.nivel, row_format)
                worksheet.write(row, 4, product.tipo_cuenta, row_format)
                worksheet.write(row, 5, product.code_parent(), row_format2)
                worksheet.write(row, 6, product.empresa.siglas, row_format)
                worksheet.write(row, 7, product.periodo, row_format)
                row += 1
            workbook.close()
            output.seek(0)
            response = HttpResponse(output,
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="Plan_Cuentas_BIO_{}.xlsx"'.format(
                datetime.now().date().strftime('%d_%m_%Y'))
            return response
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('app_planCuentas:listar_planCuenta'))


class PlanExportExcelPSMView(View):
    def get(self, request, *args, **kwargs):
        try:
            headers = {
                'id': 10,
                'CODIGO': 15,
                'NOMBRE': 75,
                'NIVEL': 20,
                'GEN_DET': 20,
                'CTA_MAY': 20,
                'EMPRESA': 20,
                'PERIODO': 20,
            }

            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('plan_cuentas')
            cell_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
            row_format = workbook.add_format({'align': 'center', 'border': 1})
            row_format2 = workbook.add_format({'align': 'left', 'border': 1})
            index = 0
            for name, width in headers.items():
                worksheet.set_column(first_col=0, last_col=index, width=width)
                worksheet.write(0, index, name, cell_format)
                index += 1
            row = 1
            queryset = PlanCuenta.objects.all()
            queryset = queryset.filter(empresa__siglas='PSM').order_by('id')
            for product in queryset:
                worksheet.write(row, 0, product.id, row_format)
                worksheet.write(row, 1, product.codigo, row_format2)
                worksheet.write(row, 2, product.nombre, row_format2)
                worksheet.write(row, 3, product.nivel, row_format)
                worksheet.write(row, 4, product.tipo_cuenta, row_format)
                worksheet.write(row, 5, product.code_parent(), row_format2)
                worksheet.write(row, 6, product.empresa.siglas, row_format)
                worksheet.write(row, 7, product.periodo, row_format)
                row += 1
            workbook.close()
            output.seek(0)
            response = HttpResponse(output,
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="Plan_Cuentas_PSM_{}.xlsx"'.format(
                datetime.now().date().strftime('%d_%m_%Y'))
            return response
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('app_planCuentas:listar_planCuenta'))



# LISTAR TRANSACCIONES DEL PLAN DE CUENTAS
class listarTransaccionPlanView(ListView):
    model = EncabezadoCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/transaccion_Plan/transaccionPlan_listar.html'

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
                for i in EncabezadoCuentasPlanCuenta.objects.filter(reg_control__exact='RT', empresa__siglas__exact='PSM'):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Transaccion de Plan de Cuentas'
        context['title'] = 'Transaccion de Plan de Cuentas'
        context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
        return context


class listarTransaccionPlanBIOView(ListView):
    model = EncabezadoCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/transaccion_Plan/transaccionPlan_listar_bio.html'

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
                for i in EncabezadoCuentasPlanCuenta.objects.filter(reg_control__exact='RT', empresa__siglas__exact='BIO'):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Transaccion de Plan de Cuentas'
        context['title'] = 'Transaccion de Plan de Cuentas'
        context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
        return context


# CREAR TRANSACCIONES DEL PLAN DE CUENTAS
class crearTransaccionPlanView(CreateView):
    model = EncabezadoCuentasPlanCuenta
    form_class = EncabezadoCuentasPlanCuentaForm
    template_name = 'app_contabilidad_planCuentas/transaccion_Plan/transaccionPlan_crear.html'
    success_url = reverse_lazy('app_planCuentas:listar_planCuenta')
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

            elif action == 'create':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    encabezado = EncabezadoCuentasPlanCuenta()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
                    encabezado.fecha = request.POST['fecha']
                    encabezado.comprobante = request.POST['comprobante']
                    encabezado.descripcion = request.POST['descripcion']
                    encabezado.direccion = request.POST['direccion']
                    encabezado.empresa_id = request.POST['empresa']
                    encabezado.save()
                    for i in items:
                        cuerpo = DetalleCuentasPlanCuenta()
                        cuerpo.encabezadocuentaplan_id = encabezado.pk
                        cuerpo.cuenta_id = int(i['id'])
                        cuerpo.detalle = i['detalle']
                        cuerpo.debe = int(i['debe']) if i.get('debe') else 0
                        cuerpo.haber = int(i['haber']) if i.get('haber') else 0
                        cuerpo.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = 'el error es : ' + str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Formulario de Registro de Transacción'
        context['list_url'] = self.success_url
        context['action'] = 'create'
        planCuenta = PlanCuenta.objects.filter(parentId=None)
        context['planCuenta'] = planCuenta
        planCuenta2 = PlanCuenta.objects.all()
        context['planCuenta2'] = planCuenta2
        context['det'] = []
        return context

# EDITAR TRANSACCIONES DEL PLAN DE CUENTAS
class editarTransaccionPlanView(UpdateView):
    model = EncabezadoCuentasPlanCuenta
    form_class = EncabezadoCuentasPlanCuentaForm
    template_name = 'app_contabilidad_planCuentas/transaccion_Plan/transaccionPlan_crear.html'
    success_url = reverse_lazy('app_planCuentas:listar_planCuenta')
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
            elif action == 'edit':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    encabezado = self.get_object()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
                    encabezado.fecha = request.POST['fecha']
                    encabezado.comprobante = request.POST['comprobante']
                    encabezado.descripcion = request.POST['descripcion']
                    encabezado.direccion = request.POST['direccion']
                    encabezado.empresa_id = request.POST['empresa']
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
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = 'el error es : ' + str(e)
        return JsonResponse(data, safe=False)

    def get_detalle(self):
        data = []
        print('self.get_object().id')
        print(self.get_object().id)
        print("self.kwargs['pk']")
        print(self.kwargs['pk'])
        for i in DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan_id=self.kwargs['pk']):
            item = i.cuenta.toJSON()
            item['detalle'] = i.detalle
            item['debe'] = format(i.debe, '.2f')
            item['haber'] = format(i.haber, '.2f')
            data.append(item)
        return json.dumps(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Formulario de Registro de Transacción'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        planCuenta = PlanCuenta.objects.filter(parentId=None)
        context['planCuenta'] = planCuenta
        planCuenta2 = PlanCuenta.objects.all()
        context['planCuenta2'] = planCuenta2
        context['det'] = self.get_detalle()
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
#
# class reporteTransaccionPlanView(View):
#
#     def get(self, request, *args, **kwargs):
#         try:
#             template = get_template('app_reportes/factura_reporte.html')
#             detalle = Producto_Stock.objects.filter(invoice_stock_id=self.kwargs['pk'])
#
#             empresa = ''
#             # fecha_ingreso = ''
#             # numero_guia = ''
#             # number = 0
#             # proveedor = ''
#
#             if detalle:
#                 empresa = detalle[0].producto_empresa.nombre_empresa
#                 # fecha_ingreso = detalle[0].invoice_stock.fecha_ingreso
#                 # numero_guia = detalle[0].invoice_stock.numero_guia
#                 # number = detalle[0].invoice_stock.id
#                 # proveedor = detalle[0].invoice_stock.proveedor
#
#             context = {
#                 'sale': InvoiceStock.objects.get(pk=self.kwargs['pk']),
#                 'comp': {'name': 'INDUSTRIA PESQUERA', 'address': 'MACHALA - EL ORO - ECUADOR',
#                          'numero': '(072) 920 371', 'comprobante': 'COMPROBANTE DE INGRESOs DE PRODUCTOS'},
#                 'icon': '{}{}'.format(settings.MEDIA_URL, 'logo.png'),
#                 'empresa': empresa,
#                 # 'detalle_fac': detalle,
#                 # 'fecha_ingreso': fecha_ingreso,
#                 # 'numero_guia': numero_guia,
#                 # 'number': number,
#                 # 'proveedor': proveedor,
#                 # 'novedad': Producto_Stock.objects.filter(invoice_stock_id=self.kwargs['pk'])
#             }
#             print('context')
#             print(context)
#             html = template.render(context)
#             css_url = os.path.join(settings.BASE_DIR, 'static/lib/bootstrap-4.4.1-dist/css/bootstrap.min.css')
#             pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(css_url)])
#             return HttpResponse(pdf, content_type='application/pdf')
#         except:
#             pass
#         return HttpResponseRedirect(reverse_lazy('app_factura:listar_factura'))


# ATS - ANEXO TRANSACCIONAL


# LISTAR ANEXO-TRANSACCIONAL
class listarAnexoTransaccionalView(ListView):
    model = EncabezadoCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/transaccion_Plan/transaccionPlan_listar.html'

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
                for i in EncabezadoCuentasPlanCuenta.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Transaccion de Plan de Cuentas'
        context['title'] = 'Transaccion de Plan de Cuentas'
        context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
        return context

# CREAR ANEXO-TRANSACCIONAL
class crearAnexoTransaccionalView(CreateView):
    model = EncabezadoCuentasPlanCuenta
    form_class = EncabezadoCuentasPlanCuentaForm
    template_name = 'app_contabilidad_planCuentas/transaccion_Plan/transaccionPlan_crear.html'
    success_url = reverse_lazy('app_planCuentas:listar_planCuenta')
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
                queryset = PlanCuenta.objects.all()
                ids_exclude = json.loads(request.POST['ids'])
                if len(ids_exclude):
                    queryset = queryset.filter().exclude(id__in=ids_exclude)
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

            elif action == 'create':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    encabezado = EncabezadoCuentasPlanCuenta()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
                    encabezado.fecha = request.POST['fecha']
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
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = 'el error es : ' + str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Formulario de Registro de Transacción'
        context['list_url'] = self.success_url
        context['action'] = 'create'
        planCuenta = PlanCuenta.objects.filter(parentId=None)
        context['planCuenta'] = planCuenta
        planCuenta2 = PlanCuenta.objects.all()
        context['planCuenta2'] = planCuenta2
        context['det'] = []
        return context

class editarAnexoTransaccionalView(UpdateView):
    model = EncabezadoCuentasPlanCuenta
    form_class = EncabezadoCuentasPlanCuentaForm
    template_name = 'app_contabilidad_planCuentas/transaccion_Plan/transaccionPlan_crear.html'
    success_url = reverse_lazy('app_planCuentas:listar_planCuenta')
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
            elif action == 'edit':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    encabezado = self.get_object()
                    encabezado.codigo = request.POST['codigo']
                    encabezado.tip_cuenta = request.POST['tip_cuenta']
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
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = 'el error es : ' + str(e)
        return JsonResponse(data, safe=False)

    def get_detalle(self):
        data = []
        # print('self.get_object().id')
        # print(self.get_object().id)
        # print("self.kwargs['pk']")
        # print(self.kwargs['pk'])
        for i in DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan_id=self.kwargs['pk']):
            item = i.cuenta.toJSON()
            item['detalle'] = i.detalle
            item['debe'] = format(i.debe, '.2f')
            item['haber'] = format(i.haber, '.2f')
            data.append(item)
        return json.dumps(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Formulario de Registro de Transacción'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        planCuenta = PlanCuenta.objects.filter(parentId=None)
        context['planCuenta'] = planCuenta
        planCuenta2 = PlanCuenta.objects.all()
        context['planCuenta2'] = planCuenta2
        context['det'] = self.get_detalle()
        return context


# LIBRO MAYOR
class listarMayorPlanView(ListView):
    model = DetalleCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/transaccion_Plan/mayorizacion/mayorizacionPlan_listar.html'

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
                detallecuenta = DetalleCuentasPlanCuenta.objects.all().order_by('cuenta__codigo')
                for i in detallecuenta:
                    data.append(i.toJSON())

            elif action == 'searchdataplan':
                print('llego a search data plan')
                data = []
                for i in PlanCuenta.objects.all().order_by('codigo'):
                    item = i.toJSON()
                    item['codigo'] = i.codigo
                    item['text'] = i.get_name()
                    data.append(item)
            # elif action == 'search_plan':
            #     print('LLEGO A SEARCH PLAN')
            #     data = []
            #     term = request.POST['term'].strip()
            #     queryset = PlanCuenta.objects.filter(codigo__icontains=term)
            #     for i in queryset:
            #         item = i.toJSON()
            #         item['codigo'] = i.codigo
            #         item['text'] = i.nombre
            #         data.append(item)
            #
            # elif action == 'search_autocomplete':
            #     print('LLEGO A SEARCH AUTOCOMPLETE')
            #     data = []
            #     term = request.POST['term']
            #     print('se extrajo parametro de term')
            #     print(term)
            #     data.append({'codigo': term, 'text': term})
            #     plan_detail = PlanCuenta.objects.filter(Q(nombre__icontains=term))[0:50]
            #     for i in plan_detail:
            #         item = i.toJSON()
            #         data.append(item)
            #
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

            elif action == 'search_report':
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                desde_rang = request.POST.get('desde_rang', '')
                hasta_rang = request.POST.get('hasta_rang', '')
                search = DetalleCuentasPlanCuenta.objects.all()
                if len(start_date) and len(end_date):
                    search = search.filter(
                        encabezadocuentaplan__fecha__range=[start_date, end_date],
                        cuenta__codigo__range=[desde_rang, hasta_rang],
                    )
                for i in search:
                    data.append(i.toJSON())

            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Libro Mayor'
        context['title'] = 'Libro Mayor'
        context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
        return context

# BALANCE PLAN
# class listarBalancePlanView(ListView):
#     model = DetalleCuentasPlanCuenta
#     template_name = 'app_contabilidad_planCuentas/balance_Plan/balance_mayorizacion_psm.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         print('request.POST')
#         print(request.POST)
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == 'searchdata_psm':
#                 data = []
#                 detallecuenta = DetalleCuentasPlanCuenta.objects.filter(cuenta__empresa__siglas__exact='PSM').order_by('cuenta__codigo')
#                 for i in detallecuenta:
#                     data.append(i.toJSON())
#
#             elif action == 'searchdataplan':
#                 print('llego a search data LIBRO DETALLE plan')
#                 data = []
#                 for i in PlanCuenta.objects.all().order_by('codigo'):
#                     item = i.toJSON()
#                     item['codigo'] = i.codigo
#                     item['text'] = i.get_name()
#                     data.append(item)
#
#             elif action == 'searchdatahierarchy':
#                 print('Generando jerarquía del plan de cuentas')
#
#                 # Construir jerarquía
#                 detallecuenta = DetalleCuentasPlanCuenta.objects.select_related('cuenta').all().order_by('cuenta__codigo')
#                 hierarchy = defaultdict(lambda: {"children": [], "cuenta": None})
#
#                 for item in detallecuenta:
#                     cuenta = item.cuenta
#                     codigo = cuenta.codigo
#                     parent_codigo = ".".join(codigo.split(".")[:-1]) if "." in codigo else None
#
#                     # Crear nodo
#                     node = {
#                         "codigo": cuenta.codigo,
#                         "nombre": cuenta.nombre,
#                         "debe": item.debe,
#                         "haber": item.haber,
#                         "saldo": item.debe - item.haber,  # Calcula el saldo
#                     }
#                     hierarchy[codigo]["cuenta"] = node
#
#                     # Agregar nodo al padre
#                     if parent_codigo:
#                         hierarchy[parent_codigo]["children"].append(hierarchy[codigo])
#
#                 # Filtrar nodos raíz
#                 data = [node for key, node in hierarchy.items() if "." not in key]
#
#             elif action == 'search_report':
#                 print('llego a search data RANGUE LIBRO DETALLE plan')
#                 data = []
#                 start_date = request.POST.get('start_date', '')
#                 end_date = request.POST.get('end_date', '')
#                 desde_rang = request.POST.get('desde_rang', '')
#                 hasta_rang = request.POST.get('hasta_rang', '')
#                 search = DetalleCuentasPlanCuenta.objects.all()
#                 if len(start_date) and len(end_date):
#                     search = search.filter(
#                         encabezadocuentaplan__fecha__range=[start_date, end_date],
#                         cuenta__codigo__range=[desde_rang, hasta_rang],
#                     )
#                 for i in search:
#                     data.append(i.toJSON())
#
#             else:
#                 data['error'] = 'Ha ocurrido un error'
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data, safe=False)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Balance de Comprobación'
#         context['title'] = 'Balance de Comprobación'
#         context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
#         return context


# ESTE ES EL QUE CASI ME GUSTO
# class listarBalancePlanView(ListView):
#     model = DetalleCuentasPlanCuenta
#     template_name = 'app_contabilidad_planCuentas/balance_Plan/balance_mayorizacion_psm.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_saldos_cuenta(self, cuenta, fecha_inicio, fecha_fin):
#         saldo_anterior = DetalleCuentasPlanCuenta.objects.filter(
#             cuenta=cuenta,
#             encabezadocuentaplan__fecha__lt=fecha_inicio
#         ).aggregate(
#             debe=Coalesce(Sum('debe'), Decimal('0')),
#             haber=Coalesce(Sum('haber'), Decimal('0'))
#         )
#
#         saldo_mes = DetalleCuentasPlanCuenta.objects.filter(
#             cuenta=cuenta,
#             encabezadocuentaplan__fecha__range=[fecha_inicio, fecha_fin]
#         ).aggregate(
#             debe=Coalesce(Sum('debe'), Decimal('0')),
#             haber=Coalesce(Sum('haber'), Decimal('0'))
#         )
#
#         saldo_actual_debe = saldo_anterior['debe'] + saldo_mes['debe']
#         saldo_actual_haber = saldo_anterior['haber'] + saldo_mes['haber']
#
#         return {
#             'saldo_anterior_debe': float(saldo_anterior['debe']),
#             'saldo_anterior_haber': float(saldo_anterior['haber']),
#             'debe': float(saldo_mes['debe']),
#             'haber': float(saldo_mes['haber']),
#             'saldo_actual_debe': float(saldo_actual_debe),
#             'saldo_actual_haber': float(saldo_actual_haber)
#         }
#
#     def get_parent_codes(self, codigo):
#         """Obtiene los códigos padre de una cuenta basado en su código"""
#         parent_codes = []
#         code = codigo
#         while len(code) > 1:
#             # Remove last segment of the code
#             code = code[:-2] if len(code) > 2 else code[:-1]
#             if code:
#                 parent_codes.append(code)
#         return parent_codes
#
#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         data = []
#         try:
#             action = request.POST.get('action')
#             if action == 'searchdata_psm':
#                 fecha_inicio = request.POST.get('fecha_inicio')
#                 fecha_fin = request.POST.get('fecha_fin')
#
#                 if not fecha_inicio or not fecha_fin:
#                     return JsonResponse({'error': 'Las fechas de inicio y fin son requeridas'}, status=400)
#
#                 try:
#                     fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
#                     fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
#                 except ValueError:
#                     return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
#
#                 # Obtener todas las cuentas ordenadas por código
#                 cuentas = PlanCuenta.objects.filter(
#                     empresa__siglas__exact='PSM'
#                 ).order_by('codigo')
#
#                 # Crear un diccionario para almacenar las cuentas por código
#                 cuentas_dict = {}
#
#                 for cuenta in cuentas:
#                     saldos = self.get_saldos_cuenta(cuenta, fecha_inicio, fecha_fin)
#
#                     # Solo incluir cuentas con movimientos o que sean cuentas mayores
#                     if (saldos['saldo_anterior_debe'] != 0 or
#                             saldos['saldo_anterior_haber'] != 0 or
#                             saldos['debe'] != 0 or
#                             saldos['haber'] != 0 or
#                             len(cuenta.codigo) <= 3):  # Cuentas mayores
#
#                         item = {
#                             'id': cuenta.id,
#                             'codigo': cuenta.codigo,
#                             'nombre': cuenta.nombre,
#                             'nivel': len(self.get_parent_codes(cuenta.codigo)) + 1,
#                             'parent_codigo': self.get_parent_codes(cuenta.codigo)[0] if self.get_parent_codes(
#                                 cuenta.codigo) else None,
#                             **saldos
#                         }
#                         data.append(item)
#                         cuentas_dict[cuenta.codigo] = item
#
#             else:
#                 return JsonResponse({'error': 'Acción no reconocida'}, status=400)
#
#         except Exception as e:
#             import traceback
#             print(traceback.format_exc())
#             return JsonResponse({'error': str(e)}, status=500)
#
#         return JsonResponse(data, safe=False)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Balance de Comprobación'
#         context['title'] = 'Balance de Comprobación'
#         context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
#         return context


class listarBalancePlanView(ListView):
    model = DetalleCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/balance_Plan/balance_mayorizacion_psm.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_saldos_cuenta(self, cuenta, fecha_inicio, fecha_fin):
        """
        Calcula los saldos de una cuenta para un período específico
        """
        # Saldo anterior: todas las transacciones hasta el día anterior a fecha_inicio
        fecha_anterior = fecha_inicio - timedelta(days=1)
        saldo_anterior = DetalleCuentasPlanCuenta.objects.filter(
            cuenta=cuenta,
            encabezadocuentaplan__fecha__lte=fecha_anterior
        ).aggregate(
            debe=Coalesce(Sum('debe'), Decimal('0')),
            haber=Coalesce(Sum('haber'), Decimal('0'))
        )

        # Saldo del mes: transacciones entre fecha_inicio y fecha_fin (inclusive)
        saldo_mes = DetalleCuentasPlanCuenta.objects.filter(
            cuenta=cuenta,
            encabezadocuentaplan__fecha__gte=fecha_inicio,
            encabezadocuentaplan__fecha__lte=fecha_fin
        ).aggregate(
            debe=Coalesce(Sum('debe'), Decimal('0')),
            haber=Coalesce(Sum('haber'), Decimal('0'))
        )

        # Para cuentas padre, incluir saldos de subcuentas
        subcuentas = PlanCuenta.objects.filter(parentId=cuenta)
        if subcuentas.exists():
            for subcuenta in subcuentas:
                sub_saldos = self.get_saldos_cuenta(subcuenta, fecha_inicio, fecha_fin)
                saldo_anterior['debe'] += Decimal(str(sub_saldos['debe_ant']))
                saldo_anterior['haber'] += Decimal(str(sub_saldos['haber_ant']))
                saldo_mes['debe'] += Decimal(str(sub_saldos['debe_mes']))
                saldo_mes['haber'] += Decimal(str(sub_saldos['haber_mes']))

        debe_actual = saldo_anterior['debe'] + saldo_mes['debe']
        haber_actual = saldo_anterior['haber'] + saldo_mes['haber']

        logger.debug(f"Cuenta: {cuenta.codigo}, Saldo anterior: {saldo_anterior}, Saldo mes: {saldo_mes}")

        return {
            'debe_ant': float(saldo_anterior['debe']),
            'haber_ant': float(saldo_anterior['haber']),
            'debe_mes': float(saldo_mes['debe']),
            'haber_mes': float(saldo_mes['haber']),
            'debe_act': float(debe_actual),
            'haber_act': float(haber_actual)
        }

    def get_account_type(self, cuenta):
        """Determina el tipo de cuenta basado en su código y naturaleza"""
        if len(cuenta.codigo) == 1:  # Cuenta mayor
            return 'G'
        elif len(cuenta.codigo) >= 9:  # Si tiene 9 o más caracteres es cuenta de detalle
            return 'D'
        else:
            return 'G'

    def get_nivel(self, codigo):
        """Determina el nivel de la cuenta basado en su código"""
        return len(codigo.split('.'))

    def get_parent_code(self, codigo):
        """Obtiene el código del padre de una cuenta"""
        parts = codigo.split('.')
        if len(parts) > 1:
            return '.'.join(parts[:-1])
        return None

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            action = request.POST.get('action')
            if action == 'searchdata_psm':
                fecha_inicio = request.POST.get('fecha_inicio')
                fecha_fin = request.POST.get('fecha_fin')
                cuenta_inicio = request.POST.get('cuenta_inicio', '1')
                cuenta_fin = request.POST.get('cuenta_fin', '9')

                if not fecha_inicio or not fecha_fin:
                    return JsonResponse({'error': 'Las fechas de inicio y fin son requeridas'}, status=400)

                try:
                    # Convertir las fechas asegurando que estén en el formato correcto
                    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

                    # Validar que fecha_fin no sea menor que fecha_inicio
                    if fecha_fin < fecha_inicio:
                        return JsonResponse({
                            'error': 'La fecha final no puede ser menor que la fecha inicial'
                        }, status=400)

                except ValueError:
                    return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

                # Obtener todas las cuentas ordenadas por código
                cuentas = PlanCuenta.objects.filter(
                    empresa__siglas__exact='PSM',
                    codigo__gte=cuenta_inicio,
                    codigo__lte=cuenta_fin
                ).order_by('codigo')

                if not cuentas.exists():
                    return JsonResponse({
                        'error': 'No se encontraron cuentas en el rango especificado'
                    }, status=404)

                data = []
                account_dict = {}

                # Primera pasada: calcular saldos para todas las cuentas
                for cuenta in cuentas:
                    saldos = self.get_saldos_cuenta(cuenta, fecha_inicio, fecha_fin)
                    nivel = self.get_nivel(cuenta.codigo)
                    tipo_cuenta = self.get_account_type(cuenta)

                    item = {
                        'id': cuenta.id,
                        'codigo': cuenta.codigo,
                        'nombre': cuenta.nombre,
                        'nivel': nivel,
                        'tipo': tipo_cuenta,
                        **saldos
                    }
                    account_dict[cuenta.codigo] = item

                # Segunda pasada: agregar saldos a cuentas padre
                for codigo, item in account_dict.items():
                    parent_code = self.get_parent_code(codigo)
                    while parent_code and parent_code in account_dict:
                        parent = account_dict[parent_code]
                        for field in ['debe_ant', 'haber_ant', 'debe_mes', 'haber_mes', 'debe_act', 'haber_act']:
                            parent[field] += item[field]
                        parent_code = self.get_parent_code(parent_code)

                # Convertir el diccionario a una lista ordenada
                data = sorted(account_dict.values(), key=lambda x: x['codigo'])

                logger.debug(f"Datos procesados: {data}")

            elif action == 'get_cuentas':
                # Obtener todas las cuentas principales (nivel 1)
                cuentas_principales = PlanCuenta.objects.filter(
                    empresa__siglas__exact='PSM',
                    codigo__regex=r'^\d+$'  # Cuentas de nivel 1 (solo dígitos)
                ).order_by('codigo')

                data = [{'codigo': cuenta.codigo, 'nombre': cuenta.nombre}
                        for cuenta in cuentas_principales]
                return JsonResponse(data, safe=False)

            else:
                return JsonResponse({'error': 'Acción no reconocida'}, status=400)

        except Exception as e:
            import traceback
            logger.error(f"Error en post: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Balance de Comprobación'
        context['title'] = 'Balance de Comprobación'
        context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
        return context




# CODIGO SI VALE SOLO EL DE ARRIBA ESTA CON CAMBIO PARA MEJORAR LA SEPARACION POR FECHA DE CORTE
# class listarBalancePlanView(ListView):
#     model = DetalleCuentasPlanCuenta
#     template_name = 'app_contabilidad_planCuentas/balance_Plan/balance_mayorizacion_psm.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_saldos_cuenta(self, cuenta, fecha_inicio, fecha_fin):
#         """
#         Calcula los saldos de una cuenta para un período específico
#         """
#         # Saldo anterior: todas las transacciones hasta fecha_inicio (exclusive)
#         saldo_anterior = DetalleCuentasPlanCuenta.objects.filter(
#             cuenta=cuenta,
#             encabezadocuentaplan__fecha__lt=fecha_inicio
#         ).aggregate(
#             debe=Coalesce(Sum('debe'), Decimal('0')),
#             haber=Coalesce(Sum('haber'), Decimal('0'))
#         )
#
#         # Saldo del mes: transacciones entre fecha_inicio y fecha_fin (inclusive)
#         saldo_mes = DetalleCuentasPlanCuenta.objects.filter(
#             cuenta=cuenta,
#             encabezadocuentaplan__fecha__gte=fecha_inicio,
#             encabezadocuentaplan__fecha__lte=fecha_fin
#         ).aggregate(
#             debe=Coalesce(Sum('debe'), Decimal('0')),
#             haber=Coalesce(Sum('haber'), Decimal('0'))
#         )
#
#         # Para cuentas padre, incluir saldos de subcuentas
#         subcuentas = PlanCuenta.objects.filter(parentId=cuenta)
#         if subcuentas.exists():
#             for subcuenta in subcuentas:
#                 sub_saldos = self.get_saldos_cuenta(subcuenta, fecha_inicio, fecha_fin)
#                 saldo_anterior['debe'] += Decimal(str(sub_saldos['debe_ant']))
#                 saldo_anterior['haber'] += Decimal(str(sub_saldos['haber_ant']))
#                 saldo_mes['debe'] += Decimal(str(sub_saldos['debe_mes']))
#                 saldo_mes['haber'] += Decimal(str(sub_saldos['haber_mes']))
#
#         debe_actual = saldo_anterior['debe'] + saldo_mes['debe']
#         haber_actual = saldo_anterior['haber'] + saldo_mes['haber']
#
#         return {
#             'debe_ant': float(saldo_anterior['debe']),
#             'haber_ant': float(saldo_anterior['haber']),
#             'debe_mes': float(saldo_mes['debe']),
#             'haber_mes': float(saldo_mes['haber']),
#             'debe_act': float(debe_actual),
#             'haber_act': float(haber_actual)
#         }
#
#     def get_account_type(self, cuenta):
#         """Determina el tipo de cuenta basado en su código y naturaleza"""
#         if len(cuenta.codigo) == 1:  # Cuenta mayor
#             return 'G'
#         elif len(cuenta.codigo) >= 9:  # Si tiene 9 o más caracteres es cuenta de detalle
#             return 'D'
#         else:
#             return 'G'
#
#     def get_nivel(self, codigo):
#         """Determina el nivel de la cuenta basado en su código"""
#         return len(codigo.split('.')[0])
#
#     def get_parent_code(self, codigo):
#         """Obtiene el código del padre de una cuenta"""
#         parts = codigo.split('.')
#         if len(parts[0]) > 1:
#             return parts[0][:-2] if len(parts[0]) > 2 else parts[0][:-1]
#         return None
#
#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         try:
#             action = request.POST.get('action')
#             if action == 'searchdata_psm':
#                 fecha_inicio = request.POST.get('fecha_inicio')
#                 fecha_fin = request.POST.get('fecha_fin')
#                 cuenta_inicio = request.POST.get('cuenta_inicio', '1')
#                 cuenta_fin = request.POST.get('cuenta_fin', '9')
#
#                 if not fecha_inicio or not fecha_fin:
#                     return JsonResponse({'error': 'Las fechas de inicio y fin son requeridas'}, status=400)
#
#                 try:
#                     # Convertir las fechas asegurando que estén en el formato correcto
#                     fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
#                     fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
#
#                     # Validar que fecha_fin no sea menor que fecha_inicio
#                     if fecha_fin < fecha_inicio:
#                         return JsonResponse({
#                             'error': 'La fecha final no puede ser menor que la fecha inicial'
#                         }, status=400)
#
#                 except ValueError:
#                     return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
#
#                 # Obtener todas las cuentas ordenadas por código
#                 cuentas = PlanCuenta.objects.filter(
#                     empresa__siglas__exact='PSM',
#                     codigo__gte=cuenta_inicio,
#                     codigo__lte=cuenta_fin
#                 ).order_by('codigo')
#
#                 if not cuentas.exists():
#                     return JsonResponse({
#                         'error': 'No se encontraron cuentas en el rango especificado'
#                     }, status=404)
#
#                 data = []
#                 account_dict = {}
#
#                 # Primera pasada: calcular saldos para todas las cuentas
#                 for cuenta in cuentas:
#                     saldos = self.get_saldos_cuenta(cuenta, fecha_inicio, fecha_fin)
#                     nivel = self.get_nivel(cuenta.codigo)
#                     tipo_cuenta = self.get_account_type(cuenta)
#
#                     item = {
#                         'id': cuenta.id,
#                         'codigo': cuenta.codigo,
#                         'nombre': cuenta.nombre,
#                         'nivel': nivel,
#                         'tipo': tipo_cuenta,
#                         **saldos
#                     }
#                     account_dict[cuenta.codigo] = item
#
#                 # Convertir el diccionario a una lista ordenada
#                 data = sorted(account_dict.values(), key=lambda x: x['codigo'])
#
#             elif action == 'get_cuentas':
#                 # Obtener todas las cuentas principales (nivel 1)
#                 cuentas_principales = PlanCuenta.objects.filter(
#                     empresa__siglas__exact='PSM',
#                     codigo__regex=r'^\d+$'  # Cuentas de nivel 1 (solo dígitos)
#                 ).order_by('codigo')
#
#                 cuentas_data = [{'codigo': cuenta.codigo, 'nombre': cuenta.nombre}
#                                 for cuenta in cuentas_principales]
#                 return JsonResponse(cuentas_data, safe=False)
#
#             else:
#                 return JsonResponse({'error': 'Acción no reconocida'}, status=400)
#
#         except Exception as e:
#             import traceback
#             print(traceback.format_exc())
#             return JsonResponse({'error': str(e)}, status=500)
#
#         return JsonResponse(data, safe=False)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Balance de Comprobación'
#         context['title'] = 'Balance de Comprobación'
#         context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
#         return context


# class listarBalancePlanView(ListView):
#     model = DetalleCuentasPlanCuenta
#     template_name = 'app_contabilidad_planCuentas/balance_Plan/balance_mayorizacion_psm.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_saldos_cuenta(self, cuenta, fecha_inicio, fecha_fin):
#         saldo_anterior = DetalleCuentasPlanCuenta.objects.filter(
#             cuenta=cuenta,
#             encabezadocuentaplan__fecha__lt=fecha_inicio
#         ).aggregate(
#             debe=Sum('debe', default=0),
#             haber=Sum('haber', default=0)
#         )
#
#         saldo_mes = DetalleCuentasPlanCuenta.objects.filter(
#             cuenta=cuenta,
#             encabezadocuentaplan__fecha__range=[fecha_inicio, fecha_fin]
#         ).aggregate(
#             debe=Sum('debe', default=0),
#             haber=Sum('haber', default=0)
#         )
#
#         saldo_actual_debe = saldo_anterior['debe'] + saldo_mes['debe']
#         saldo_actual_haber = saldo_anterior['haber'] + saldo_mes['haber']
#
#         return {
#             'saldo_anterior_debe': float(saldo_anterior['debe']),
#             'saldo_anterior_haber': float(saldo_anterior['haber']),
#             'debe': float(saldo_mes['debe']),
#             'haber': float(saldo_mes['haber']),
#             'saldo_actual_debe': float(saldo_actual_debe),
#             'saldo_actual_haber': float(saldo_actual_haber)
#         }
#
#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST.get('action')
#             if action == 'searchdata_psm':
#                 fecha_inicio = request.POST.get('fecha_inicio')
#                 fecha_fin = request.POST.get('fecha_fin')
#
#                 if not fecha_inicio or not fecha_fin:
#                     return JsonResponse({'error': 'Las fechas de inicio y fin son requeridas'}, status=400)
#
#                 try:
#                     fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
#                     fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
#                 except ValueError:
#                     return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
#
#                 cuentas = PlanCuenta.objects.filter(empresa__siglas__exact='PSM').order_by('codigo')
#
#                 data = []
#                 for cuenta in cuentas:
#                     saldos = self.get_saldos_cuenta(cuenta, fecha_inicio, fecha_fin)
#
#                     if (saldos['saldo_anterior_debe'] != 0 or
#                             saldos['saldo_anterior_haber'] != 0 or
#                             saldos['debe'] != 0 or
#                             saldos['haber'] != 0):
#                         item = {
#                             'cuenta': {
#                                 'codigo': cuenta.codigo,
#                                 'nombre': cuenta.nombre
#                             },
#                             **saldos
#                         }
#                         data.append(item)
#
#             elif action == 'searchdataplan':
#                 data = []
#                 for cuenta in PlanCuenta.objects.filter(empresa__siglas__exact='PSM').order_by('codigo'):
#                     data.append({
#                         'codigo': cuenta.codigo,
#                         'nombre': cuenta.nombre,
#                         'text': f"{cuenta.codigo} - {cuenta.nombre}"
#                     })
#
#             else:
#                 data = {'error': 'Acción no reconocida'}
#                 return JsonResponse(data, status=400)
#
#         except Exception as e:
#             data = {'error': str(e)}
#             return JsonResponse(data, status=500)
#
#         return JsonResponse(data, safe=False)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Balance de Comprobación'
#         context['title'] = 'Balance de Comprobación'
#         context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
#         return context



# class listarBalancePlanView(ListView):
#     model = DetalleCuentasPlanCuenta
#     template_name = 'app_contabilidad_planCuentas/balance_Plan/balance_mayorizacion_psm.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_saldos_cuenta(self, cuenta, fecha_inicio, fecha_fin):
#         try:
#             saldo_anterior = DetalleCuentasPlanCuenta.objects.filter(
#                 cuenta=cuenta,
#                 encabezadocuentaplan__fecha__lt=fecha_inicio
#             ).aggregate(
#                 debe=Sum('debe', default=0),
#                 haber=Sum('haber', default=0)
#             )
#
#             saldo_mes = DetalleCuentasPlanCuenta.objects.filter(
#                 cuenta=cuenta,
#                 encabezadocuentaplan__fecha__range=[fecha_inicio, fecha_fin]
#             ).aggregate(
#                 debe=Sum('debe', default=0),
#                 haber=Sum('haber', default=0)
#             )
#
#             return {
#                 'saldo_anterior_debe': float(saldo_anterior['debe'] or 0),
#                 'saldo_anterior_haber': float(saldo_anterior['haber'] or 0),
#                 'debe': float(saldo_mes['debe'] or 0),
#                 'haber': float(saldo_mes['haber'] or 0),
#                 'saldo_actual_debe': float((saldo_anterior['debe'] or 0) + (saldo_mes['debe'] or 0)),
#                 'saldo_actual_haber': float((saldo_anterior['haber'] or 0) + (saldo_mes['haber'] or 0))
#             }
#         except Exception as e:
#             print(f"Error calculando saldos para cuenta {cuenta.codigo}: {str(e)}")
#             return {
#                 'saldo_anterior_debe': 0,
#                 'saldo_anterior_haber': 0,
#                 'debe': 0,
#                 'haber': 0,
#                 'saldo_actual_debe': 0,
#                 'saldo_actual_haber': 0
#             }
#
#     def process_account_hierarchy(self, cuenta, fecha_inicio, fecha_fin, processed_accounts=None):
#         if processed_accounts is None:
#             processed_accounts = set()
#
#         if cuenta.codigo in processed_accounts:
#             return None
#
#         processed_accounts.add(cuenta.codigo)
#
#         saldos = self.get_saldos_cuenta(cuenta, fecha_inicio, fecha_fin)
#
#         # Solo incluir la cuenta si tiene movimientos o es una cuenta total
#         if (saldos['saldo_anterior_debe'] != 0 or
#                 saldos['saldo_anterior_haber'] != 0 or
#                 saldos['debe'] != 0 or
#                 saldos['haber'] != 0 or
#                 cuenta.band_total):
#
#             account_data = {
#                 'cuenta': {
#                     'codigo': cuenta.codigo,
#                     'nombre': cuenta.nombre,
#                     'nivel': cuenta.nivel
#                 },
#                 'is_total': cuenta.band_total,
#                 **saldos
#             }
#
#             # Procesar cuentas hijas
#             children = PlanCuenta.objects.filter(parentId=cuenta).order_by('codigo')
#             if children.exists():
#                 account_data['children'] = []
#                 for child in children:
#                     child_data = self.process_account_hierarchy(child, fecha_inicio, fecha_fin, processed_accounts)
#                     if child_data:
#                         account_data['children'].append(child_data)
#
#             return account_data
#         return None
#
#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST.get('action')
#             if action == 'searchdata_psm':
#                 fecha_inicio = request.POST.get('fecha_inicio')
#                 fecha_fin = request.POST.get('fecha_fin')
#
#                 if not fecha_inicio or not fecha_fin:
#                     return JsonResponse({'error': 'Las fechas de inicio y fin son requeridas'}, status=400)
#
#                 try:
#                     self.fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
#                     self.fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
#                 except ValueError:
#                     return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
#
#                 # Obtener cuentas raíz (nivel 1)
#                 root_accounts = PlanCuenta.objects.filter(
#                     empresa__siglas__exact='PSM',
#                     nivel=1
#                 ).order_by('codigo')
#
#                 data = []
#                 processed_accounts = set()
#
#                 for root_account in root_accounts:
#                     account_data = self.process_account_hierarchy(
#                         root_account,
#                         self.fecha_inicio,
#                         self.fecha_fin,
#                         processed_accounts
#                     )
#                     if account_data:
#                         data.append(account_data)
#
#             elif action == 'searchdataplan':
#                 data = []
#                 for cuenta in PlanCuenta.objects.filter(
#                         empresa__siglas__exact='PSM'
#                 ).order_by('codigo'):
#                     data.append({
#                         'codigo': cuenta.codigo,
#                         'nombre': cuenta.nombre,
#                         'text': f"{cuenta.codigo} - {cuenta.nombre}"
#                     })
#             else:
#                 return JsonResponse({'error': 'Acción no reconocida'}, status=400)
#
#         except Exception as e:
#             import traceback
#             print(traceback.format_exc())
#             return JsonResponse({'error': str(e)}, status=500)
#
#         return JsonResponse(data, safe=False)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Balance de Comprobación'
#         context['title'] = 'Balance de Comprobación'
#         context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
#         return context

class listarBalancePlanBIOView(ListView):
    model = DetalleCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/balance_Plan/balance_mayorizacion_bio.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_saldos_cuenta(self, cuenta, fecha_inicio, fecha_fin):
        """
        Calcula los saldos de una cuenta para un período específico
        """
        # Saldo anterior: todas las transacciones hasta fecha_inicio (exclusive)
        saldo_anterior = DetalleCuentasPlanCuenta.objects.filter(
            cuenta=cuenta,
            encabezadocuentaplan__fecha__lt=fecha_inicio
        ).aggregate(
            debe=Coalesce(Sum('debe'), Decimal('0')),
            haber=Coalesce(Sum('haber'), Decimal('0'))
        )

        # Saldo del mes: transacciones entre fecha_inicio y fecha_fin (inclusive)
        saldo_mes = DetalleCuentasPlanCuenta.objects.filter(
            cuenta=cuenta,
            encabezadocuentaplan__fecha__gte=fecha_inicio,
            encabezadocuentaplan__fecha__lte=fecha_fin
        ).aggregate(
            debe=Coalesce(Sum('debe'), Decimal('0')),
            haber=Coalesce(Sum('haber'), Decimal('0'))
        )

        # Para cuentas padre, incluir saldos de subcuentas
        subcuentas = PlanCuenta.objects.filter(parentId=cuenta)
        if subcuentas.exists():
            for subcuenta in subcuentas:
                sub_saldos = self.get_saldos_cuenta(subcuenta, fecha_inicio, fecha_fin)
                saldo_anterior['debe'] += Decimal(str(sub_saldos['debe_ant']))
                saldo_anterior['haber'] += Decimal(str(sub_saldos['haber_ant']))
                saldo_mes['debe'] += Decimal(str(sub_saldos['debe_mes']))
                saldo_mes['haber'] += Decimal(str(sub_saldos['haber_mes']))

        debe_actual = saldo_anterior['debe'] + saldo_mes['debe']
        haber_actual = saldo_anterior['haber'] + saldo_mes['haber']

        return {
            'debe_ant': float(saldo_anterior['debe']),
            'haber_ant': float(saldo_anterior['haber']),
            'debe_mes': float(saldo_mes['debe']),
            'haber_mes': float(saldo_mes['haber']),
            'debe_act': float(debe_actual),
            'haber_act': float(haber_actual)
        }

    def get_account_type(self, cuenta):
        """Determina el tipo de cuenta basado en su código y naturaleza"""
        if len(cuenta.codigo) == 1:  # Cuenta mayor
            return 'G'
        elif len(cuenta.codigo) >= 9:  # Si tiene 9 o más caracteres es cuenta de detalle
            return 'D'
        else:
            return 'G'

    def get_nivel(self, codigo):
        """Determina el nivel de la cuenta basado en su código"""
        return len(codigo.split('.')[0])

    def get_parent_code(self, codigo):
        """Obtiene el código del padre de una cuenta"""
        parts = codigo.split('.')
        if len(parts[0]) > 1:
            return parts[0][:-2] if len(parts[0]) > 2 else parts[0][:-1]
        return None

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            action = request.POST.get('action')
            if action == 'searchdata_bio':
                fecha_inicio = request.POST.get('fecha_inicio')
                fecha_fin = request.POST.get('fecha_fin')
                cuenta_inicio = request.POST.get('cuenta_inicio', '1')
                cuenta_fin = request.POST.get('cuenta_fin', '9')

                if not fecha_inicio or not fecha_fin:
                    return JsonResponse({'error': 'Las fechas de inicio y fin son requeridas'}, status=400)

                try:
                    # Convertir las fechas asegurando que estén en el formato correcto
                    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

                    # Validar que fecha_fin no sea menor que fecha_inicio
                    if fecha_fin < fecha_inicio:
                        return JsonResponse({
                            'error': 'La fecha final no puede ser menor que la fecha inicial'
                        }, status=400)

                except ValueError:
                    return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

                # Obtener todas las cuentas ordenadas por código
                cuentas = PlanCuenta.objects.filter(
                    empresa__siglas__exact='BIO',
                    codigo__gte=cuenta_inicio,
                    codigo__lte=cuenta_fin
                ).order_by('codigo')

                if not cuentas.exists():
                    return JsonResponse({
                        'error': 'No se encontraron cuentas en el rango especificado'
                    }, status=404)

                data = []
                account_dict = {}

                # Primera pasada: calcular saldos para todas las cuentas
                for cuenta in cuentas:
                    saldos = self.get_saldos_cuenta(cuenta, fecha_inicio, fecha_fin)
                    nivel = self.get_nivel(cuenta.codigo)
                    tipo_cuenta = self.get_account_type(cuenta)

                    item = {
                        'id': cuenta.id,
                        'codigo': cuenta.codigo,
                        'nombre': cuenta.nombre,
                        'nivel': nivel,
                        'tipo': tipo_cuenta,
                        **saldos
                    }
                    account_dict[cuenta.codigo] = item

                # Convertir el diccionario a una lista ordenada
                data = sorted(account_dict.values(), key=lambda x: x['codigo'])

            elif action == 'get_cuentas':
                # Obtener todas las cuentas principales (nivel 1)
                cuentas_principales = PlanCuenta.objects.filter(
                    empresa__siglas__exact='BIO',
                    codigo__regex=r'^\d+$'  # Cuentas de nivel 1 (solo dígitos)
                ).order_by('codigo')

                cuentas_data = [{'codigo': cuenta.codigo, 'nombre': cuenta.nombre} for cuenta in cuentas_principales]
                return JsonResponse(cuentas_data, safe=False)

            else:
                return JsonResponse({'error': 'Acción no reconocida'}, status=400)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Balance de Comprobación'
        context['title'] = 'Balance de Comprobación'
        context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
        return context

# class listarBalancePlanBIOView(ListView):
#     model = DetalleCuentasPlanCuenta
#     template_name = 'app_contabilidad_planCuentas/balance_Plan/balance_mayorizacion_bio.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         print('request.POST')
#         print(request.POST)
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == 'searchdata_bio':
#                 data = []
#                 detallecuenta = DetalleCuentasPlanCuenta.objects.filter(cuenta__empresa__siglas__exact='BIO').order_by('cuenta__codigo')
#                 for i in detallecuenta:
#                     data.append(i.toJSON())
#
#             elif action == 'searchdataplan':
#                 print('llego a search data LIBRO DETALLE plan')
#                 data = []
#                 for i in PlanCuenta.objects.all().order_by('codigo'):
#                     item = i.toJSON()
#                     item['codigo'] = i.codigo
#                     item['text'] = i.get_name()
#                     data.append(item)
#
#             elif action == 'searchdatahierarchy':
#                 print('Generando jerarquía del plan de cuentas')
#
#                 # Construir jerarquía
#                 detallecuenta = DetalleCuentasPlanCuenta.objects.select_related('cuenta').all().order_by('cuenta__codigo')
#                 hierarchy = defaultdict(lambda: {"children": [], "cuenta": None})
#
#                 for item in detallecuenta:
#                     cuenta = item.cuenta
#                     codigo = cuenta.codigo
#                     parent_codigo = ".".join(codigo.split(".")[:-1]) if "." in codigo else None
#
#                     # Crear nodo
#                     node = {
#                         "codigo": cuenta.codigo,
#                         "nombre": cuenta.nombre,
#                         "debe": item.debe,
#                         "haber": item.haber,
#                         "saldo": item.debe - item.haber,  # Calcula el saldo
#                     }
#                     hierarchy[codigo]["cuenta"] = node
#
#                     # Agregar nodo al padre
#                     if parent_codigo:
#                         hierarchy[parent_codigo]["children"].append(hierarchy[codigo])
#
#                 # Filtrar nodos raíz
#                 data = [node for key, node in hierarchy.items() if "." not in key]
#
#             elif action == 'search_report':
#                 print('llego a search data RANGUE LIBRO DETALLE plan')
#                 data = []
#                 start_date = request.POST.get('start_date', '')
#                 end_date = request.POST.get('end_date', '')
#                 desde_rang = request.POST.get('desde_rang', '')
#                 hasta_rang = request.POST.get('hasta_rang', '')
#                 search = DetalleCuentasPlanCuenta.objects.all()
#                 if len(start_date) and len(end_date):
#                     search = search.filter(
#                         encabezadocuentaplan__fecha__range=[start_date, end_date],
#                         cuenta__codigo__range=[desde_rang, hasta_rang],
#                     )
#                 for i in search:
#                     data.append(i.toJSON())
#
#             else:
#                 data['error'] = 'Ha ocurrido un error'
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data, safe=False)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Balance de Comprobación'
#         context['title'] = 'Balance de Comprobación'
#         context['list_url'] = reverse_lazy('app_planCuentas:listar_transaccionPlan')
#         return context


class DiarioGeneralAcumuladoPSMView(ListView):
    model = EncabezadoCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/diario_general/diario_acumuladoPSM.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                empresa = request.POST['empresa']
                fecha_inicio = request.POST.get('fecha_inicio', '2024-12-01')
                fecha_fin = request.POST.get('fecha_fin', '2025-01-31')

                asientos = DetalleCuentasPlanCuenta.objects.select_related(
                    'cuenta',
                    'encabezadocuentaplan'
                ).filter(
                    encabezadocuentaplan__empresa__siglas__exact=empresa,
                    encabezadocuentaplan__fecha__range=[fecha_inicio, fecha_fin]
                ).order_by(
                    'encabezadocuentaplan__fecha',
                    'encabezadocuentaplan__id',
                    'orden'
                )

                data = self.process_asientos(asientos)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def process_asientos(self, asientos):
        total_general_debe = 0
        total_general_haber = 0
        fecha_actual = None
        asientos_agrupados = []
        subtotal_debe = 0
        subtotal_haber = 0

        for asiento in asientos:
            if fecha_actual != asiento.encabezadocuentaplan.fecha:
                if fecha_actual is not None:
                    asientos_agrupados.append({
                        'tipo': 'total',
                        'fecha': fecha_actual.strftime('%Y-%m-%d'),
                        'codigo': '',
                        'nombre': '',
                        'doc': '',
                        'descripcion': 'TOTAL FECHA ................',
                        'debe': float(subtotal_debe),
                        'haber': float(subtotal_haber)
                    })
                fecha_actual = asiento.encabezadocuentaplan.fecha
                subtotal_debe = 0
                subtotal_haber = 0

            asientos_agrupados.append({
                'tipo': 'asiento',
                'fecha': asiento.encabezadocuentaplan.fecha.strftime('%Y-%m-%d'),
                'codigo': asiento.cuenta.codigo,
                'nombre': asiento.cuenta.nombre,
                'doc': asiento.encabezadocuentaplan.comprobante,
                'descripcion': asiento.detalle or asiento.encabezadocuentaplan.descripcion,
                'debe': float(asiento.debe),
                'haber': float(asiento.haber)
            })

            subtotal_debe += asiento.debe
            subtotal_haber += asiento.haber
            total_general_debe += asiento.debe
            total_general_haber += asiento.haber

        if fecha_actual is not None:
            asientos_agrupados.append({
                'tipo': 'total',
                'fecha': fecha_actual.strftime('%Y-%m-%d'),
                'codigo': '',
                'nombre': '',
                'doc': '',
                'descripcion': 'TOTAL FECHA ................',
                'debe': float(subtotal_debe),
                'haber': float(subtotal_haber)
            })

        return {
            'asientos': asientos_agrupados,
            'total_general': {
                'tipo': 'grand_total',
                'fecha': '',
                'codigo': '',
                'nombre': '',
                'doc': '',
                'descripcion': 'TOTAL DEL REPORTE....',
                'debe': float(total_general_debe),
                'haber': float(total_general_haber)
            }
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Diario General Acumulado'
        context['list_url'] = reverse_lazy('diario_general:diario_acumulado')
        # context['empresa_id'] = self.kwargs['empresa_id']
        # context['empresa_nombre'] = Empresa.objects.get(id=self.kwargs['empresa_id']).nombre
        return context


class DiarioGeneralAcumuladoBIOView(ListView):
    model = EncabezadoCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/diario_general/diario_acumuladoPSM.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                empresa = request.POST['empresa']
                fecha_inicio = request.POST.get('fecha_inicio', '2024-12-01')
                fecha_fin = request.POST.get('fecha_fin', '2025-01-31')

                asientos = DetalleCuentasPlanCuenta.objects.select_related(
                    'cuenta',
                    'encabezadocuentaplan'
                ).filter(
                    encabezadocuentaplan__empresa__siglas__exact=empresa,
                    encabezadocuentaplan__fecha__range=[fecha_inicio, fecha_fin]
                ).order_by(
                    'encabezadocuentaplan__fecha',
                    'encabezadocuentaplan__id',
                    'orden'
                )

                data = self.process_asientos(asientos)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def process_asientos(self, asientos):
        total_general_debe = 0
        total_general_haber = 0
        fecha_actual = None
        asientos_agrupados = []
        subtotal_debe = 0
        subtotal_haber = 0

        for asiento in asientos:
            if fecha_actual != asiento.encabezadocuentaplan.fecha:
                if fecha_actual is not None:
                    asientos_agrupados.append({
                        'tipo': 'total',
                        'fecha': fecha_actual.strftime('%Y-%m-%d'),
                        'codigo': '',
                        'nombre': '',
                        'doc': '',
                        'descripcion': 'TOTAL FECHA ................',
                        'debe': float(subtotal_debe),
                        'haber': float(subtotal_haber)
                    })
                fecha_actual = asiento.encabezadocuentaplan.fecha
                subtotal_debe = 0
                subtotal_haber = 0

            asientos_agrupados.append({
                'tipo': 'asiento',
                'fecha': asiento.encabezadocuentaplan.fecha.strftime('%Y-%m-%d'),
                'codigo': asiento.cuenta.codigo,
                'nombre': asiento.cuenta.nombre,
                'doc': asiento.encabezadocuentaplan.comprobante,
                'descripcion': asiento.detalle or asiento.encabezadocuentaplan.descripcion,
                'debe': float(asiento.debe),
                'haber': float(asiento.haber)
            })

            subtotal_debe += asiento.debe
            subtotal_haber += asiento.haber
            total_general_debe += asiento.debe
            total_general_haber += asiento.haber

        if fecha_actual is not None:
            asientos_agrupados.append({
                'tipo': 'total',
                'fecha': fecha_actual.strftime('%Y-%m-%d'),
                'codigo': '',
                'nombre': '',
                'doc': '',
                'descripcion': 'TOTAL FECHA ................',
                'debe': float(subtotal_debe),
                'haber': float(subtotal_haber)
            })

        return {
            'asientos': asientos_agrupados,
            'total_general': {
                'tipo': 'grand_total',
                'fecha': '',
                'codigo': '',
                'nombre': '',
                'doc': '',
                'descripcion': 'TOTAL DEL REPORTE....',
                'debe': float(total_general_debe),
                'haber': float(total_general_haber)
            }
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Diario General Acumulado'
        context['list_url'] = reverse_lazy('diario_general:diario_acumulado')
        # context['empresa_id'] = self.kwargs['empresa_id']
        # context['empresa_nombre'] = Empresa.objects.get(id=self.kwargs['empresa_id']).nombre
        return context