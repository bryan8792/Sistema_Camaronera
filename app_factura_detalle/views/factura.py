
import json
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, View
from weasyprint import HTML, CSS
from app_stock.app_detalle_stock.forms import ProdStockForm
from app_stock.app_detalle_stock.models import Producto_Stock, Total_Stock, InvoiceStock


class listarFacturaView(ListView):
    model = InvoiceStock
    template_name = 'app_factura_detalle/factura_detalle_listar.html'

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
                for i in InvoiceStock.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Facturas de Compra'
        context['title'] = 'Listado de Factura de Compra'
        # context['create_url'] = reverse_lazy('erp:sale_create')
        context['list_url'] = reverse_lazy('app_factura:listar_factura')
        context['entity'] = 'Ventas'
        return context


class crearFacturaView(CreateView):
    model = Producto_Stock
    form_class = ProdStockForm
    template_name = 'app_factura_detalle/factura_detalle_crear.html'
    success_url = reverse_lazy('app_factura:listar_factura')
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = []
                empresa = request.POST['empresa']
                queryset = Total_Stock.objects.filter()
                ids_exclude = json.loads(request.POST['ids'])
                queryset = queryset.filter(nombre_empresa__siglas=empresa).exclude(id__in=ids_exclude)
                for i in queryset:
                    item = i.toJSON()
                    item['cantidad_usar'] = 0
                    item['cantidad_ingreso'] = 0
                    data.append(item)
            elif action == 'create':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    factura = InvoiceStock()
                    factura.user = request.user
                    factura.fecha_ingreso = request.POST['fecha_ingreso']
                    factura.numero_guia = request.POST['numero_guia']
                    factura.responsable_ingreso = request.POST['responsable_ingreso']
                    factura.proveedor_id = request.POST['proveedor']
                    factura.observacion = request.POST['observacion']
                    factura.subtotal = request.POST['subtotal']
                    factura.iva = request.POST['iva']
                    factura.ivacalc = request.POST['ivacalc']
                    factura.total = request.POST['total']
                    factura.save()
                    for i in items:
                        inv = Producto_Stock()
                        inv.invoice_stock = factura
                        inv.producto_empresa_id = int(i['id'])
                        inv.cantidad_usar = float(i['cantidad_usar'])
                        inv.cantidad_ingreso = float(i['cantidad_ingreso'])
                        inv.subtotal = float(i['subtotal'])
                        inv.fecha_ingreso = request.POST['fecha_ingreso']
                        inv.numero_guia = request.POST['numero_guia']
                        inv.responsable_ingreso = request.POST['responsable_ingreso']
                        inv.proveedor_id = request.POST['proveedor']
                        inv.observacion = request.POST['observacion']
                        inv.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Facturas de Compra'
        context['entity'] = 'Factura'
        context['list_url'] = self.success_url
        context['action'] = 'create'
        context['det'] = []
        return context


class editarFacturaView(UpdateView):
    model = InvoiceStock
    form_class = ProdStockForm
    template_name = 'app_factura_detalle/factura_detalle_crear.html'
    success_url = reverse_lazy('app_factura:listar_factura')
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
            if action == 'search_products':
                data = []
                empresa = request.POST['empresa']
                queryset = Total_Stock.objects.filter()
                ids_exclude = json.loads(request.POST['ids'])
                queryset = queryset.filter(nombre_empresa__siglas=empresa).exclude(id__in=ids_exclude)
                for i in queryset:
                    item = i.toJSON()
                    item['cantidad_usar'] = 0
                    item['cantidad_ingreso'] = 0
                    data.append(item)
            elif action == 'edit':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    factura = self.get_object()
                    factura.user = request.user
                    factura.fecha_ingreso = request.POST['fecha_ingreso']
                    factura.numero_guia = request.POST['numero_guia']
                    factura.responsable_ingreso = request.POST['responsable_ingreso']
                    factura.proveedor_id = request.POST['proveedor']
                    factura.observacion = request.POST['observacion']
                    factura.subtotal = request.POST['subtotal']
                    factura.iva = request.POST['iva']
                    factura.ivacalc = request.POST['ivacalc']
                    factura.total = request.POST['total']
                    factura.save()
                    for s in factura.producto_stock_set.all():
                        s.producto_empresa.stock = float(s.producto_empresa.stock) - float(s.cantidad_ingreso)
                        s.producto_empresa.save()
                        s.delete()
                    for i in items:
                        inv = Producto_Stock()
                        inv.invoice_stock = factura
                        inv.producto_empresa_id = int(i['id'])
                        inv.cantidad_usar = float(i['cantidad_usar'])
                        inv.cantidad_ingreso = float(i['cantidad_ingreso'])
                        inv.subtotal = float(i['subtotal'])
                        inv.fecha_ingreso = request.POST['fecha_ingreso']
                        inv.numero_guia = request.POST['numero_guia']
                        inv.responsable_ingreso = request.POST['responsable_ingreso']
                        inv.proveedor_id = request.POST['proveedor']
                        inv.observacion = request.POST['observacion']
                        inv.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_detalle(self):
        data = []
        for i in Producto_Stock.objects.filter(invoice_stock_id=self.kwargs['pk']):
            item = i.producto_empresa.toJSON()
            item['cantidad_usar'] = format(i.cantidad_usar, '.2f')
            item['cantidad_ingreso'] = format(i.cantidad_ingreso, '.2f')
            item['cantidad_egreso'] = format(i.cantidad_egreso, '.2f')
            data.append(item)
        return json.dumps(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Facturas de Compra'
        context['entity'] = 'Factura'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['det'] = self.get_detalle()
        return context


class eliminarFacturaView(DeleteView):
    model = InvoiceStock
    template_name = 'app_factura_detalle/factura_detalle_eliminar.html'
    success_url = reverse_lazy('app_factura:listar_factura')
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de una Factura'
        context['entity'] = 'Factura'
        context['list_url'] = reverse_lazy('app_factura:listar_factura')
        return context



class SaleInvoicePdfView(View):

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('app_reportes/factura_reporte.html')
            detalle = Producto_Stock.objects.filter(invoice_stock_id=self.kwargs['pk'])

            empresa = ''
            # fecha_ingreso = ''
            # numero_guia = ''
            # number = 0
            # proveedor = ''

            if detalle:
                empresa = detalle[0].producto_empresa.nombre_empresa
                # fecha_ingreso = detalle[0].invoice_stock.fecha_ingreso
                # numero_guia = detalle[0].invoice_stock.numero_guia
                # number = detalle[0].invoice_stock.id
                # proveedor = detalle[0].invoice_stock.proveedor

            context = {
                'sale': InvoiceStock.objects.get(pk=self.kwargs['pk']),
                'comp': {'name': 'INDUSTRIA PESQUERA', 'address': 'MACHALA - EL ORO - ECUADOR',
                         'numero': '(072) 920 371', 'comprobante': 'COMPROBANTE DE INGRESOs DE PRODUCTOS'},
                'icon': '{}{}'.format(settings.MEDIA_URL, 'logo.png'),
                'empresa': empresa,
                # 'detalle_fac': detalle,
                # 'fecha_ingreso': fecha_ingreso,
                # 'numero_guia': numero_guia,
                # 'number': number,
                # 'proveedor': proveedor,
                # 'novedad': Producto_Stock.objects.filter(invoice_stock_id=self.kwargs['pk'])
            }
            print('context')
            print(context)
            html = template.render(context)
            css_url = os.path.join(settings.BASE_DIR, 'static/lib/bootstrap-4.4.1-dist/css/bootstrap.min.css')
            pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(css_url)])
            return HttpResponse(pdf, content_type='application/pdf')
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('app_factura:listar_factura'))


class SaleInvoicePdfSuperView(View):

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('app_reportes/factura_reporte_super.html')
            detalle = Producto_Stock.objects.filter(invoice_stock_id=self.kwargs['pk'])

            empresa = ''
            # fecha_ingreso = ''
            # numero_guia = ''
            # number = 0
            # proveedor = ''

            if detalle:
                empresa = detalle[0].producto_empresa.nombre_empresa
                # fecha_ingreso = detalle[0].invoice_stock.fecha_ingreso
                # numero_guia = detalle[0].invoice_stock.numero_guia
                # number = detalle[0].invoice_stock.id
                # proveedor = detalle[0].invoice_stock.proveedor

            context = {
                'sale': InvoiceStock.objects.get(pk=self.kwargs['pk']),
                'comp': {'name': 'INDUSTRIA PESQUERA', 'address': 'MACHALA - EL ORO - ECUADOR',
                         'numero': '(072) 920 371', 'comprobante': 'COMPROBANTE DE INGRESOS DE PRODUCTOS'},
                'icon': '{}{}'.format(settings.MEDIA_URL, 'logo.png'),
                'empresa': empresa,
                # 'detalle_fac': detalle,
                # 'fecha_ingreso': fecha_ingreso,
                # 'numero_guia': numero_guia,
                # 'number': number,
                # 'proveedor': proveedor,
                # 'novedad': Producto_Stock.objects.filter(invoice_stock_id=self.kwargs['pk'])
            }
            html = template.render(context)
            css_url = os.path.join(settings.BASE_DIR, 'static/lib/bootstrap-4.4.1-dist/css/bootstrap.min.css')
            pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(css_url)])
            return HttpResponse(pdf, content_type='application/pdf')
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('app_factura:listar_factura'))
