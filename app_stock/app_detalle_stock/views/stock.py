
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.utils import timezone
from datetime import datetime
from app_contabilidad_planCuentas.models import PlanCuenta, DetalleCuentasPlanCuenta, EncabezadoCuentasPlanCuenta
from app_dieta.app_dieta_reg.models import DetalleDiaDieta
from app_empresa.app_piscinas.models import Piscinas
from app_empresa.app_reg_empresa.models import Empresa
from app_inventario.app_categoria.models import Producto
from app_reportes.utils import render_to_pdf
from app_stock.app_detalle_stock.forms import ProdStockForm, ProdStockTotalForm, StockAccountingForm
from app_stock.app_detalle_stock.models import Producto_Stock, Total_Stock, InvoiceStock
import decimal
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import F
from datetime import datetime
import re
from django.db.models import Sum, Q
from datetime import datetime, date
from collections import defaultdict
from decimal import Decimal


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


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class CrearStockConCuentaBIOView(CreateView):
    """
    Update existing stock with accounting plan selection
    Actualiza el registro existente de Total_Stock asignándole plan de cuentas
    """
    model = Total_Stock
    form_class = StockAccountingForm
    template_name = 'app_stock/stock_crear_con_cuenta_bio.html'
    success_url = reverse_lazy('app_stock:listar_stock_bio')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        empresa_id = self.request.GET.get('empresa_id') or self.kwargs.get('empresa_id')
        producto_id = self.request.GET.get('producto_id')

        if empresa_id and producto_id:
            try:
                empresa = Empresa.objects.get(pk=empresa_id)
                producto = Producto.objects.get(pk=producto_id)
                kwargs['initial'] = {
                    'nombre_empresa': empresa,
                    'nombre_prod': producto
                }
                kwargs['empresa_obj'] = empresa
                kwargs['producto_obj'] = producto
                kwargs['readonly_mode'] = True
            except (Empresa.DoesNotExist, Producto.DoesNotExist):
                pass
        elif empresa_id:
            try:
                empresa = Empresa.objects.get(pk=empresa_id)
                kwargs['initial'] = {'nombre_empresa': empresa}
                kwargs['empresa_obj'] = empresa
            except Empresa.DoesNotExist:
                pass
        return kwargs

    def form_valid(self, form):
        empresa_id = self.kwargs.get('empresa_id') or self.request.GET.get('empresa_id')
        producto_id = self.request.GET.get('producto_id') or self.request.POST.get('nombre_prod')
        plan_cuenta_id = self.request.POST.get('plan_cuenta')

        if not empresa_id or not producto_id:
            form.add_error(None, 'Faltan parámetros de empresa o producto')
            return self.form_invalid(form)

        try:
            empresa = Empresa.objects.get(pk=empresa_id)
            producto = Producto.objects.get(pk=producto_id)
            plan_cuenta = PlanCuenta.objects.get(pk=plan_cuenta_id) if plan_cuenta_id else None

            # Find existing Total_Stock record
            stock_existente = Total_Stock.objects.filter(
                nombre_empresa=empresa,
                nombre_prod=producto
            ).first()

            if stock_existente:
                # UPDATE existing record
                stock_existente.plan_cuenta = plan_cuenta
                if plan_cuenta:
                    stock_existente.cod_contable = plan_cuenta.codigo
                stock_existente.save(update_fields=['plan_cuenta', 'cod_contable'])
                self.object = stock_existente
            else:
                # CREATE new record if doesn't exist
                self.object = Total_Stock.objects.create(
                    nombre_empresa=empresa,
                    nombre_prod=producto,
                    plan_cuenta=plan_cuenta,
                    cod_contable=plan_cuenta.codigo if plan_cuenta else None,
                    stock=0
                )

            return redirect(self.success_url)

        except (Empresa.DoesNotExist, Producto.DoesNotExist, PlanCuenta.DoesNotExist) as e:
            form.add_error(None, f'Error: {str(e)}')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get parameters from URL kwargs and GET params
        empresa_id = self.kwargs.get('empresa_id') or self.request.GET.get('empresa_id')
        producto_id = self.request.GET.get('producto_id')

        if not empresa_id or not producto_id:
            context['error'] = 'No se proporcionaron los parámetros de empresa y producto.'
            return context

        try:
            empresa = Empresa.objects.get(pk=empresa_id)
            producto = Producto.objects.get(pk=producto_id)

            context['empresa'] = empresa
            context['producto'] = producto
            context['readonly_mode'] = True

            # Get plan de cuentas for this empresa
            context['plan_cuentas'] = PlanCuenta.objects.filter(
                empresa=empresa,
                estado=True
            ).order_by('codigo')

            # Get stock information
            try:
                stock = Total_Stock.objects.get(
                    nombre_empresa=empresa,
                    nombre_prod=producto
                )
                context['stock_actual'] = stock.stock
                context['cuenta_actual'] = stock.plan_cuenta
            except Total_Stock.DoesNotExist:
                context['stock_actual'] = 0.00
                context['cuenta_actual'] = None

        except (Empresa.DoesNotExist, Producto.DoesNotExist) as e:
            context['error'] = f'No se encontró la empresa o producto: {str(e)}'

        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class CrearStockConCuentaPSMView(CreateView):
    """
    Update existing stock with accounting plan selection
    Actualiza el registro existente de Total_Stock asignándole plan de cuentas
    """
    model = Total_Stock
    form_class = StockAccountingForm
    template_name = 'app_stock/stock_crear_con_cuenta_psm.html'
    success_url = reverse_lazy('app_stock:listar_stock_psm')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        empresa_id = self.request.GET.get('empresa_id') or self.kwargs.get('empresa_id')
        producto_id = self.request.GET.get('producto_id')

        if empresa_id and producto_id:
            try:
                empresa = Empresa.objects.get(pk=empresa_id)
                producto = Producto.objects.get(pk=producto_id)
                kwargs['initial'] = {
                    'nombre_empresa': empresa,
                    'nombre_prod': producto
                }
                kwargs['empresa_obj'] = empresa
                kwargs['producto_obj'] = producto
                kwargs['readonly_mode'] = True
            except (Empresa.DoesNotExist, Producto.DoesNotExist):
                pass
        elif empresa_id:
            try:
                empresa = Empresa.objects.get(pk=empresa_id)
                kwargs['initial'] = {'nombre_empresa': empresa}
                kwargs['empresa_obj'] = empresa
            except Empresa.DoesNotExist:
                pass
        return kwargs

    def form_valid(self, form):
        empresa_id = self.kwargs.get('empresa_id') or self.request.GET.get('empresa_id')
        producto_id = self.request.GET.get('producto_id') or self.request.POST.get('nombre_prod')
        plan_cuenta_id = self.request.POST.get('plan_cuenta')

        if not empresa_id or not producto_id:
            form.add_error(None, 'Faltan parámetros de empresa o producto')
            return self.form_invalid(form)

        try:
            empresa = Empresa.objects.get(pk=empresa_id)
            producto = Producto.objects.get(pk=producto_id)
            plan_cuenta = PlanCuenta.objects.get(pk=plan_cuenta_id) if plan_cuenta_id else None

            # Find existing Total_Stock record
            stock_existente = Total_Stock.objects.filter(
                nombre_empresa=empresa,
                nombre_prod=producto
            ).first()

            if stock_existente:
                # UPDATE existing record
                stock_existente.plan_cuenta = plan_cuenta
                if plan_cuenta:
                    stock_existente.cod_contable = plan_cuenta.codigo
                stock_existente.save(update_fields=['plan_cuenta', 'cod_contable'])
                self.object = stock_existente
            else:
                # CREATE new record if doesn't exist
                self.object = Total_Stock.objects.create(
                    nombre_empresa=empresa,
                    nombre_prod=producto,
                    plan_cuenta=plan_cuenta,
                    cod_contable=plan_cuenta.codigo if plan_cuenta else None,
                    stock=0
                )

            return redirect(self.success_url)

        except (Empresa.DoesNotExist, Producto.DoesNotExist, PlanCuenta.DoesNotExist) as e:
            form.add_error(None, f'Error: {str(e)}')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get parameters from URL kwargs and GET params
        empresa_id = self.kwargs.get('empresa_id') or self.request.GET.get('empresa_id')
        producto_id = self.request.GET.get('producto_id')

        if not empresa_id or not producto_id:
            context['error'] = 'No se proporcionaron los parámetros de empresa y producto.'
            return context

        try:
            empresa = Empresa.objects.get(pk=empresa_id)
            producto = Producto.objects.get(pk=producto_id)

            context['empresa'] = empresa
            context['producto'] = producto
            context['readonly_mode'] = True

            # Get plan de cuentas for this empresa
            context['plan_cuentas'] = PlanCuenta.objects.filter(
                empresa=empresa,
                estado=True
            ).order_by('codigo')

            # Get stock information
            try:
                stock = Total_Stock.objects.get(
                    nombre_empresa=empresa,
                    nombre_prod=producto
                )
                context['stock_actual'] = stock.stock
                context['cuenta_actual'] = stock.plan_cuenta
            except Total_Stock.DoesNotExist:
                context['stock_actual'] = 0.00
                context['cuenta_actual'] = None

        except (Empresa.DoesNotExist, Producto.DoesNotExist) as e:
            context['error'] = f'No se encontró la empresa o producto: {str(e)}'

        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class EditarStockConCuentaView(UpdateView):
    """
    Edit stock with accounting plan selection
    Permite editar un producto de stock y cambiar su plan de cuentas
    """
    model = Total_Stock
    form_class = StockAccountingForm
    template_name = 'app_stock/stock_editar_con_cuenta.html'
    success_url = reverse_lazy('app_stock:listar_stock_bio')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Automatically save the accounting plan code
        if self.object.plan_cuenta:
            self.object.cod_contable = self.object.plan_cuenta.codigo
            self.object.save(update_fields=['cod_contable'])
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plan_cuentas'] = PlanCuenta.objects.filter(
            empresa=self.object.nombre_empresa,
            estado=True
        ).order_by('codigo')
        return context


@login_required
@csrf_exempt
def get_cuentas_por_empresa(request):
    """
    AJAX endpoint to load accounting plans by company
    Retorna lista de cuentas contables para una empresa específica
    """
    empresa_id = request.GET.get('empresa_id')

    if not empresa_id:
        return JsonResponse({'error': 'Empresa no especificada'}, status=400)

    try:
        empresa = Empresa.objects.get(pk=empresa_id)
        cuentas = PlanCuenta.objects.filter(
            empresa=empresa,
            estado=True,
            nivel__lte=5  # Limit to operational accounts (not summary accounts)
        ).values('id', 'codigo', 'nombre', 'get_full_hierarchy').order_by('codigo')

        return JsonResponse({
            'success': True,
            'cuentas': list(cuentas)
        })
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Empresa no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def get_productos_por_empresa(request):
    """
    AJAX endpoint to load products that have stock for a specific company
    Retorna productos que tienen registros en Total_Stock para una empresa
    """
    empresa_id = request.GET.get('empresa_id')

    if not empresa_id:
        return JsonResponse({'error': 'Empresa no especificada'}, status=400)

    try:
        empresa = Empresa.objects.get(pk=empresa_id)

        # Get productos that have stock records for this empresa
        productos_ids = Total_Stock.objects.filter(
            nombre_empresa=empresa
        ).values_list('nombre_prod_id', flat=True).distinct()

        productos = Producto.objects.filter(
            id__in=productos_ids,
            estado=True
        ).values('id', 'nombre_producto').order_by('nombre_producto')

        productos_list = [
            {
                'id': p['id'],
                'nombre': p['nombre_producto']
            }
            for p in productos
        ]

        return JsonResponse({
            'success': True,
            'productos': productos_list
        })
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Empresa no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def get_stock_info(request):
    """
    AJAX endpoint to get current stock information
    Retorna información del stock actual para un producto y empresa
    """
    empresa_id = request.GET.get('empresa_id')
    producto_id = request.GET.get('producto_id')

    if not empresa_id or not producto_id:
        return JsonResponse({'error': 'Parámetros incompletos'}, status=400)

    try:
        stock = Total_Stock.objects.get(
            nombre_empresa_id=empresa_id,
            nombre_prod_id=producto_id
        )

        cuenta_actual = None
        if stock.plan_cuenta:
            cuenta_actual = f"{stock.plan_cuenta.codigo} - {stock.plan_cuenta.nombre}"

        return JsonResponse({
            'success': True,
            'producto_nombre': stock.nombre_prod.nombre_producto,
            'stock': float(stock.stock),
            'cuenta_actual': cuenta_actual,
            'cod_contable': stock.cod_contable
        })
    except Total_Stock.DoesNotExist:
        return JsonResponse({'error': 'Stock no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_empresa_from_piscina(numero_piscina):
    """
    Determine company based on pool number
    Piscinas 1-20 = PSM
    Piscinas 21-45 = BIO
    """
    try:
        # Extract number from piscina name if needed
        if isinstance(numero_piscina, str):
            num = int(''.join(filter(str.isdigit, numero_piscina)))
        else:
            num = numero_piscina

        if 1 <= num <= 20:
            return 'PSM'
        elif 21 <= num <= 45:
            return 'BIO'
        else:
            return None
    except (ValueError, TypeError):
        return None


# @receiver(post_save, sender=Producto_Stock)
# def crear_asiento_contable_egreso(sender, instance, created, **kwargs):
#     """
#     Signal que crea automáticamente asientos contables cuando hay un EGRESO de stock
#     """
#
#     if not created or instance.tipo != 'EGRESO':
#         return
#
#     print(f"\n{'=' * 60}")
#     print(f"[CONTABILIDAD] INICIANDO PROCESO DE ASIENTO CONTABLE")
#     print(f"{'=' * 60}")
#
#     try:
#         print(f"[CONTABILIDAD] ID Producto_Stock: {instance.id}")
#         print(f"[CONTABILIDAD] Tipo: {instance.tipo}")
#         print(f"[CONTABILIDAD] Cantidad egreso: {instance.cantidad_egreso}")
#
#         piscina_obj = instance.piscinas
#         if not piscina_obj:
#             print(f"[CONTABILIDAD] ERROR: No hay piscina asignada")
#             return
#
#         piscina_nombre = str(piscina_obj)
#         print(f"[CONTABILIDAD] Piscina: {piscina_nombre}")
#
#         match = re.search(r'\d+', piscina_nombre)
#         if not match:
#             print(f"[CONTABILIDAD] ERROR: No se pudo extraer número de piscina")
#             return
#
#         piscina_numero = int(match.group())
#         print(f"[CONTABILIDAD] Piscina número: {piscina_numero}")
#
#         empresa_siglas = 'PSM' if 1 <= piscina_numero <= 20 else 'BIO' if 21 <= piscina_numero <= 45 else None
#         if not empresa_siglas:
#             print(f"[CONTABILIDAD] ERROR: Piscina fuera de rango")
#             return
#
#         print(f"[CONTABILIDAD] Empresa: {empresa_siglas}")
#
#         print(f"[CONTABILIDAD] Buscando empresa...")
#         try:
#             empresa_obj = Empresa.objects.filter(siglas=empresa_siglas).first()
#             print(f"[CONTABILIDAD] Empresa query ejecutada: {empresa_obj}")
#         except Exception as e:
#             print(f"[CONTABILIDAD] ERROR en query Empresa: {e}")
#             return
#
#         if not empresa_obj:
#             print(f"[CONTABILIDAD] ERROR: Empresa no encontrada")
#             return
#
#         print(f"[CONTABILIDAD] Empresa OK: {empresa_obj.nombre}")
#
#         print(f"[CONTABILIDAD] Buscando producto...")
#         try:
#             producto_id = instance.producto_empresa.nombre_prod.id
#             print(f"[CONTABILIDAD] Producto ID: {producto_id}")
#         except Exception as e:
#             print(f"[CONTABILIDAD] ERROR accediendo a producto: {e}")
#             import traceback
#             traceback.print_exc()
#             return
#
#         print(f"[CONTABILIDAD] Buscando Total_Stock...")
#         try:
#             stock_total = Total_Stock.objects.filter(
#                 nombre_prod__id=producto_id,
#                 nombre_empresa__id=empresa_obj.id
#             ).first()
#             print(f"[CONTABILIDAD] Total_Stock: {stock_total}")
#         except Exception as e:
#             print(f"[CONTABILIDAD] ERROR en query Total_Stock: {e}")
#             import traceback
#             traceback.print_exc()
#             return
#
#         if not stock_total or not stock_total.plan_cuenta:
#             print(f"[CONTABILIDAD] ERROR: Producto sin plan de cuentas")
#             return
#
#         cuenta_producto = stock_total.plan_cuenta
#         print(f"[CONTABILIDAD] Cuenta producto: {cuenta_producto.codigo}")
#
#         print(f"[CONTABILIDAD] Buscando cuenta SUMINISTROS...")
#         cuenta_suministros = None
#
#         if hasattr(piscina_obj, 'cuenta_suministros') and piscina_obj.cuenta_suministros:
#             cuenta_suministros = piscina_obj.cuenta_suministros
#             print(f"[CONTABILIDAD] Cuenta SUMINISTROS (FK): {cuenta_suministros.codigo}")
#         else:
#             # Buscar por nombre
#             cuenta_piscina = None
#             for formato in [f'PISCINA#{piscina_numero}', f'PISCINA# {piscina_numero}']:
#                 cuenta_piscina = PlanCuenta.objects.filter(
#                     empresa=empresa_obj,
#                     nombre__icontains=formato,
#                     estado=True
#                 ).first()
#                 if cuenta_piscina:
#                     break
#
#             if not cuenta_piscina:
#                 print(f"[CONTABILIDAD] ERROR: No existe cuenta piscina")
#                 return
#
#             cuenta_suministros = PlanCuenta.objects.filter(
#                 empresa=empresa_obj,
#                 parentId=cuenta_piscina,
#                 nombre__iexact='SUMINISTROS',
#                 estado=True
#             ).first()
#
#             if not cuenta_suministros:
#                 print(f"[CONTABILIDAD] ERROR: No existe subcuenta SUMINISTROS")
#                 return
#
#         print(f"[CONTABILIDAD] Cuenta SUMINISTROS: {cuenta_suministros.codigo}")
#
#         monto = float(instance.cantidad_egreso or 0)
#         if monto <= 0:
#             print(f"[CONTABILIDAD] ERROR: Monto inválido")
#             return
#
#         print(f"[CONTABILIDAD] Monto: ${monto:.2f}")
#
#         print(f"[CONTABILIDAD] Creando encabezado...")
#         encabezado = EncabezadoCuentasPlanCuenta.objects.create(
#             codigo=int(datetime.now().timestamp()),
#             tip_cuenta='5',
#             tip_transa='EGRESO',
#             fecha=instance.fecha_ingreso or timezone.now().date(),
#             comprobante=f"EGR-{instance.id}-P{piscina_numero}",
#             descripcion=f"Consumo en Piscina {piscina_numero}",
#             empresa=empresa_obj,
#             reg_control='RT'
#         )
#         print(f"[CONTABILIDAD] Encabezado creado ID: {encabezado.id}")
#
#         detalle_debe = DetalleCuentasPlanCuenta.objects.create(
#             encabezadocuentaplan=encabezado,
#             orden=1,
#             cuenta=cuenta_suministros,
#             detalle=f"Consumo P#{piscina_numero}",
#             debe=monto,
#             haber=0.00,
#             origen='STOCK'
#         )
#         print(f"[CONTABILIDAD] DEBE creado ID: {detalle_debe.id} - ${monto} - ${detalle_debe.orden}")
#
#         detalle_haber = DetalleCuentasPlanCuenta.objects.create(
#             encabezadocuentaplan=encabezado,
#             orden=2,
#             cuenta=cuenta_producto,
#             detalle=f"Egreso inventario",
#             debe=0.00,
#             haber=monto,
#             origen='STOCK'
#         )
#         print(f"[CONTABILIDAD] HABER creado ID: {detalle_haber.id} - ${monto}")
#
#         print(f"{'=' * 60}")
#         print(f"[CONTABILIDAD] ASIENTO CONTABLE CREADO EXITOSAMENTE")
#         print(f"[CONTABILIDAD] Comprobante: {encabezado.comprobante}")
#         print(f"{'=' * 60}\n")
#
#     except Exception as e:
#         print(f"{'=' * 60}")
#         print(f"[CONTABILIDAD] ERROR CRITICO EN SIGNAL")
#         print(f"[CONTABILIDAD] Error: {type(e).__name__}: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         print(f"{'=' * 60}\n")


# @receiver(post_save, sender=Producto_Stock)
# def crear_asiento_contable_egreso(sender, instance, created, **kwargs):
#     """
#     Crea o RECREA asientos contables por EGRESOS de stock asociados a DIETAS.
#     Diseñado para PRODUCCIÓN.
#     """
#
#     # ─────────────────────────────
#     # VALIDACIONES BASE
#     # ─────────────────────────────
#     if not created:
#         return
#
#     if instance.tipo != 'EGRESO':
#         return
#
#     if not instance.detalle_dieta_id:
#         return
#
#     piscina = instance.piscinas
#     if not piscina:
#         return
#
#     # ─────────────────────────────
#     # EMPRESA DESDE LA PISCINA (CORRECTO)
#     # ─────────────────────────────
#     empresa = getattr(piscina, 'empresa', None)
#     if not empresa:
#         return
#
#     # ─────────────────────────────
#     # CUENTA DEL PRODUCTO (INVENTARIO)
#     # ─────────────────────────────
#     producto = instance.producto_empresa.nombre_prod
#
#     stock_total = Total_Stock.objects.filter(
#         nombre_prod=producto,
#         nombre_empresa=empresa
#     ).first()
#
#     if not stock_total or not stock_total.plan_cuenta:
#         return
#
#     cuenta_producto = stock_total.plan_cuenta
#
#     # ─────────────────────────────
#     # CUENTA SUMINISTROS (DESDE PISCINA)
#     # ─────────────────────────────
#     cuenta_suministros = getattr(piscina, 'cuenta_suministros', None)
#     if not cuenta_suministros:
#         return
#
#     # ─────────────────────────────
#     # MONTO
#     # ─────────────────────────────
#     monto = float(instance.cantidad_egreso or 0)
#     if monto <= 0:
#         return
#
#     comprobante = f"EGR-DET-{instance.detalle_dieta_id}"
#
#     print("\n" + "=" * 60)
#     print("[CONTABILIDAD] PROCESO ASIENTO DIETA")
#     print("=" * 60)
#
#     with transaction.atomic():
#
#         # ─────────────────────────────
#         # ELIMINAR ASIENTOS ANTERIORES
#         # ─────────────────────────────
#         encabezados_previos = EncabezadoCuentasPlanCuenta.objects.filter(
#             comprobante=comprobante,
#             empresa=empresa
#         )
#
#         if encabezados_previos.exists():
#             print(f"[CONTABILIDAD] Eliminando asientos previos ({comprobante})")
#             encabezados_previos.delete()
#
#         # ─────────────────────────────
#         # CREAR ENCABEZADO
#         # ─────────────────────────────
#         encabezado = EncabezadoCuentasPlanCuenta.objects.create(
#             codigo=int(datetime.now().timestamp()),
#             tip_cuenta='5',
#             tip_transa='EGRESO',
#             fecha=instance.fecha_ingreso or timezone.now().date(),
#             comprobante=comprobante,
#             descripcion=f"Consumo Dieta Piscina {piscina}",
#             empresa=empresa,
#             reg_control='RT'
#         )
#
#         # ─────────────────────────────
#         # DEBE – SUMINISTROS
#         # ─────────────────────────────
#         DetalleCuentasPlanCuenta.objects.create(
#             encabezadocuentaplan=encabezado,
#             orden=1,
#             cuenta=cuenta_suministros,
#             detalle=f"Consumo dieta {piscina}",
#             debe=monto,
#             haber=0,
#             origen='STOCK'
#         )
#
#         # ─────────────────────────────
#         # HABER – INVENTARIO
#         # ─────────────────────────────
#         DetalleCuentasPlanCuenta.objects.create(
#             encabezadocuentaplan=encabezado,
#             orden=2,
#             cuenta=cuenta_producto,
#             detalle="Egreso de inventario",
#             debe=0,
#             haber=monto,
#             origen='STOCK'
#         )
#
#         print(f"[CONTABILIDAD] Asiento recreado correctamente ({comprobante})")




# @receiver(post_save, sender=Producto_Stock)
# def crear_asiento_contable_egreso(sender, instance, created, **kwargs):
#     """
#     Signal que crea automáticamente asientos contables cuando hay un EGRESO de stock
#     AJUSTADO PARA EDICIÓN DE DIETA (elimina asientos previos)
#     """
#
#     # 🔴 VALIDACIONES BASE (NO SE TOCAN)
#     if not created or instance.tipo != 'EGRESO':
#         return
#
#     # 🔴 SOLO PARA DIETAS (CLAVE)
#     if not instance.detalle_dieta_id:
#         return
#
#     print(f"\n{'=' * 60}")
#     print(f"[CONTABILIDAD] INICIANDO PROCESO DE ASIENTO CONTABLE (DIETA)")
#     print(f"{'=' * 60}")
#
#     try:
#         piscina_obj = instance.piscinas
#         if not piscina_obj:
#             return
#
#         piscina_nombre = str(piscina_obj)
#         match = re.search(r'\d+', piscina_nombre)
#         if not match:
#             return
#
#         piscina_numero = int(match.group())
#
#         empresa_siglas = 'PSM' if 1 <= piscina_numero <= 20 else 'BIO' if 21 <= piscina_numero <= 45 else None
#         if not empresa_siglas:
#             return
#
#         empresa_obj = Empresa.objects.filter(siglas=empresa_siglas).first()
#         if not empresa_obj:
#             return
#
#         producto_id = instance.producto_empresa.nombre_prod.id
#
#         stock_total = Total_Stock.objects.filter(
#             nombre_prod__id=producto_id,
#             nombre_empresa__id=empresa_obj.id
#         ).first()
#
#         if not stock_total or not stock_total.plan_cuenta:
#             return
#
#         cuenta_producto = stock_total.plan_cuenta
#
#         # CUENTA SUMINISTROS
#         cuenta_suministros = None
#         if hasattr(piscina_obj, 'cuenta_suministros') and piscina_obj.cuenta_suministros:
#             cuenta_suministros = piscina_obj.cuenta_suministros
#         else:
#             cuenta_piscina = None
#             for formato in [f'PISCINA#{piscina_numero}', f'PISCINA# {piscina_numero}']:
#                 cuenta_piscina = PlanCuenta.objects.filter(
#                     empresa=empresa_obj,
#                     nombre__icontains=formato,
#                     estado=True
#                 ).first()
#                 if cuenta_piscina:
#                     break
#
#             if not cuenta_piscina:
#                 return
#
#             cuenta_suministros = PlanCuenta.objects.filter(
#                 empresa=empresa_obj,
#                 parentId=cuenta_piscina,
#                 nombre__iexact='SUMINISTROS',
#                 estado=True
#             ).first()
#
#             if not cuenta_suministros:
#                 return
#
#         monto = float(instance.cantidad_egreso or 0)
#         if monto <= 0:
#             return
#
#         # 🔴 🔴 🔴 MEJORA CLAVE 🔴 🔴 🔴
#         # BORRAR ASIENTOS CONTABLES ANTERIORES DE ESTA DIETA
#         comprobante_ref = f"EGR-DET-{instance.detalle_dieta_id}"
#
#         encabezados_previos = EncabezadoCuentasPlanCuenta.objects.filter(
#             comprobante=comprobante_ref,
#             empresa=empresa_obj
#         )
#
#         if encabezados_previos.exists():
#             print(f"[CONTABILIDAD] Eliminando asientos anteriores de dieta {instance.detalle_dieta_id}")
#             encabezados_previos.delete()
#
#         # 🔴 CREAR NUEVO ENCABEZADO
#         encabezado = EncabezadoCuentasPlanCuenta.objects.create(
#             codigo=int(datetime.now().timestamp()),
#             tip_cuenta='5',
#             tip_transa='EGRESO',
#             fecha=instance.fecha_ingreso or timezone.now().date(),
#             comprobante=comprobante_ref,
#             descripcion=f"Consumo Dieta Piscina {piscina_numero}",
#             empresa=empresa_obj,
#             reg_control='RT'
#         )
#
#         # DEBE
#         DetalleCuentasPlanCuenta.objects.create(
#             encabezadocuentaplan=encabezado,
#             orden=1,
#             cuenta=cuenta_suministros,
#             detalle=f"Consumo Piscina {piscina_numero}",
#             debe=monto,
#             haber=0.00,
#             origen='STOCK'
#         )
#
#         # HABER
#         DetalleCuentasPlanCuenta.objects.create(
#             encabezadocuentaplan=encabezado,
#             orden=2,
#             cuenta=cuenta_producto,
#             detalle="Egreso inventario",
#             debe=0.00,
#             haber=monto,
#             origen='STOCK'
#         )
#
#         print(f"[CONTABILIDAD] Asiento recreado correctamente ({comprobante_ref})")
#
#     except Exception as e:
#         print(f"[CONTABILIDAD] ERROR CRÍTICO")
#         import traceback
#         traceback.print_exc()

#
# def connect_signals():
#     """
#     Connect all signals - call this in apps.py ready() method
#     """
#     pass

#
# def eliminar_asientos_por_detalle(detalle_id):
#     encabezados = EncabezadoCuentasPlanCuenta.objects.filter(
#         comprobante__icontains=f"EGR-DET-{detalle_id}"
#     )
#
#     for e in encabezados:
#         DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan=e).delete()
#         e.delete()


class ListarAsientosContablesView(ListView):
    model = EncabezadoCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/asientos_contables/asientos_contables_listar.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action', '')

            if action == 'get_asiento_detalle':
                # Obtener detalles de un asiento específico
                asiento_id = request.POST.get('id')
                asiento = EncabezadoCuentasPlanCuenta.objects.get(pk=asiento_id)
                detalles = DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan=asiento).select_related('cuenta')

                data = {
                    'encabezado': {
                        'codigo': asiento.codigo,
                        'fecha': asiento.fecha.strftime('%Y-%m-%d') if asiento.fecha else '',
                        'descripcion': asiento.descripcion,
                        'comprobante': asiento.comprobante,
                    },
                    'detalles': [
                        {
                            'cuenta': d.cuenta.codigo if d.cuenta else '',
                            'nombre_cuenta': d.cuenta.nombre if d.cuenta else '',
                            'detalle': d.detalle,
                            'debe': float(d.debe) if d.debe else 0,
                            'haber': float(d.haber) if d.haber else 0,
                        } for d in detalles
                    ]
                }

        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtros de fecha
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        empresa_id = self.request.GET.get('empresa')

        # Query base - solo asientos de stock
        query = Q(tip_transa='EGRESO') | Q(descripcion__icontains='Consumo')

        if fecha_desde:
            query &= Q(fecha__gte=fecha_desde)
        if fecha_hasta:
            query &= Q(fecha__lte=fecha_hasta)
        if empresa_id:
            query &= Q(empresa_id=empresa_id)

        # Asientos con sus detalles
        asientos = EncabezadoCuentasPlanCuenta.objects.filter(query).select_related('empresa'
        ).prefetch_related('detallecuentasplancuenta_set__cuenta').order_by('-fecha', '-codigo')

        # Calcular totales
        total_debe = 0
        total_haber = 0
        asientos_data = []

        for asiento in asientos:
            detalles = asiento.detallecuentasplancuenta_set.all()
            debe_asiento = sum(d.debe or 0 for d in detalles)
            haber_asiento = sum(d.haber or 0 for d in detalles)

            total_debe += debe_asiento
            total_haber += haber_asiento

            asientos_data.append({
                'asiento': asiento,
                'detalles': detalles,
                'debe': debe_asiento,
                'haber': haber_asiento,
            })

        context['nombre'] = 'Asientos Contables de Consumo'
        context['asientos_data'] = asientos_data
        context['total_debe'] = total_debe
        context['total_haber'] = total_haber
        context['fecha_desde'] = fecha_desde
        context['fecha_hasta'] = fecha_hasta
        return context


class ListarAsientosContablesBIOView(ListView):
    model = EncabezadoCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/asientos_contables/asientos_contables_listar_bio.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action', '')

            if action == 'get_asiento_detalle':
                asiento_id = request.POST.get('id')
                asiento = EncabezadoCuentasPlanCuenta.objects.get(pk=asiento_id)
                detalles = DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan=asiento).select_related('cuenta')

                data = {
                    'encabezado': {
                        'codigo': asiento.codigo,
                        'fecha': asiento.fecha.strftime('%Y-%m-%d') if asiento.fecha else '',
                        'descripcion': asiento.descripcion,
                        'comprobante': asiento.comprobante,
                    },
                    'detalles': [
                        {
                            'cuenta': d.cuenta.codigo if d.cuenta else '',
                            'nombre_cuenta': d.cuenta.nombre if d.cuenta else '',
                            'detalle': d.detalle,
                            'debe': float(d.debe) if d.debe else 0,
                            'haber': float(d.haber) if d.haber else 0,
                        } for d in detalles
                    ]
                }

        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtros de fecha
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')

        # Query base - filtrar por empresa con siglas "BIO"
        query = Q(empresa__siglas='BIO')  # <-- Filtro por siglas de empresa
        query &= Q(tip_transa='EGRESO') | Q(descripcion__icontains='Consumo')

        if fecha_desde:
            query &= Q(fecha__gte=fecha_desde)
        if fecha_hasta:
            query &= Q(fecha__lte=fecha_hasta)

        # Asientos con sus detalles
        asientos = EncabezadoCuentasPlanCuenta.objects.filter(query).select_related('empresa'
        ).prefetch_related('detallecuentasplancuenta_set__cuenta').order_by('-fecha', '-codigo')

        # Calcular totales
        total_debe = 0
        total_haber = 0
        asientos_data = []

        for asiento in asientos:
            detalles = asiento.detallecuentasplancuenta_set.all()
            debe_asiento = sum(d.debe or 0 for d in detalles)
            haber_asiento = sum(d.haber or 0 for d in detalles)

            total_debe += debe_asiento
            total_haber += haber_asiento

            asientos_data.append({
                'asiento': asiento,
                'detalles': detalles,
                'debe': debe_asiento,
                'haber': haber_asiento,
            })

        context['nombre'] = 'Asientos Contables de Consumo - Empresa BIO'
        context['asientos_data'] = asientos_data
        context['total_debe'] = total_debe
        context['total_haber'] = total_haber
        context['fecha_desde'] = fecha_desde
        context['fecha_hasta'] = fecha_hasta
        return context


class ListarAsientosContablesPSMView(ListView):
    model = EncabezadoCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/asientos_contables/asientos_contables_listar_psm.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action', '')

            if action == 'get_asiento_detalle':
                asiento_id = request.POST.get('id')
                asiento = EncabezadoCuentasPlanCuenta.objects.get(pk=asiento_id)
                detalles = DetalleCuentasPlanCuenta.objects.filter(encabezadocuentaplan=asiento).select_related('cuenta')

                data = {
                    'encabezado': {
                        'codigo': asiento.codigo,
                        'fecha': asiento.fecha.strftime('%Y-%m-%d') if asiento.fecha else '',
                        'descripcion': asiento.descripcion,
                        'comprobante': asiento.comprobante,
                    },
                    'detalles': [
                        {
                            'cuenta': d.cuenta.codigo if d.cuenta else '',
                            'nombre_cuenta': d.cuenta.nombre if d.cuenta else '',
                            'detalle': d.detalle,
                            'debe': float(d.debe) if d.debe else 0,
                            'haber': float(d.haber) if d.haber else 0,
                        } for d in detalles
                    ]
                }

        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtros de fecha
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')

        # Query base - filtrar por empresa con siglas "PSM"
        query = Q(empresa__siglas='PSM')  # <-- Filtro por siglas de empresa
        query &= Q(tip_transa='EGRESO') | Q(descripcion__icontains='Consumo')

        if fecha_desde:
            query &= Q(fecha__gte=fecha_desde)
        if fecha_hasta:
            query &= Q(fecha__lte=fecha_hasta)

        # Asientos con sus detalles
        asientos = EncabezadoCuentasPlanCuenta.objects.filter(query).select_related('empresa'
        ).prefetch_related('detallecuentasplancuenta_set__cuenta').order_by('-fecha', '-codigo')

        # Calcular totales
        total_debe = 0
        total_haber = 0
        asientos_data = []

        for asiento in asientos:
            detalles = asiento.detallecuentasplancuenta_set.all()
            debe_asiento = sum(d.debe or 0 for d in detalles)
            haber_asiento = sum(d.haber or 0 for d in detalles)

            total_debe += debe_asiento
            total_haber += haber_asiento

            asientos_data.append({
                'asiento': asiento,
                'detalles': detalles,
                'debe': debe_asiento,
                'haber': haber_asiento,
            })

        context['nombre'] = 'Asientos Contables de Consumo - Empresa PSM'
        context['asientos_data'] = asientos_data
        context['total_debe'] = total_debe
        context['total_haber'] = total_haber
        context['fecha_desde'] = fecha_desde
        context['fecha_hasta'] = fecha_hasta
        return context


class ReporteAsientosContablesView(ListView):
    model = DetalleCuentasPlanCuenta
    template_name = 'app_contabilidad_planCuentas/asientos_contables/reporte_asientos_contables.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Detalle Asientos Contables por Consumo de Inventario'

        # Obtener parámetros de filtro
        fecha_desde = self.request.GET.get('fecha_desde', date.today().replace(day=1).strftime('%Y-%m-%d'))
        fecha_hasta = self.request.GET.get('fecha_hasta', date.today().strftime('%Y-%m-%d'))
        empresa_id = self.request.GET.get('empresa', '')

        context['fecha_desde'] = fecha_desde
        context['fecha_hasta'] = fecha_hasta
        context['empresa_seleccionada'] = empresa_id
        context['empresas'] = Empresa.objects.all()

        # Filtrar encabezados por fecha y tipo
        query = Q(tip_cuenta='EGRESO DE INVENTARIO')
        query &= Q(fecha__gte=fecha_desde)
        query &= Q(fecha__lte=fecha_hasta)

        if empresa_id:
            query &= Q(empresa_id=empresa_id)

        # Obtener encabezados de asientos contables
        encabezados = EncabezadoCuentasPlanCuenta.objects.filter(query).order_by('fecha', 'codigo')

        # Agrupar por piscina
        asientos_agrupados = {}
        total_general = 0

        for encabezado in encabezados:
            # Obtener detalles del asiento
            detalles = DetalleCuentasPlanCuenta.objects.filter(
                encabezado_cuenta=encabezado
            ).select_related('cuenta')

            # Extraer número de piscina del comprobante (formato: EGR-123-P21)
            piscina = 'N/A'
            if encabezado.comprobante:
                partes = encabezado.comprobante.split('-')
                if len(partes) >= 3:
                    piscina = partes[2]  # P21, P22, etc.

            if piscina not in asientos_agrupados:
                asientos_agrupados[piscina] = {
                    'numero': piscina,
                    'asientos': [],
                    'subtotal': 0
                }

            # Calcular total del asiento (suma de débitos)
            total_asiento = detalles.filter(debe__gt=0).aggregate(Sum('debe'))['debe__sum'] or 0

            asientos_agrupados[piscina]['asientos'].append({
                'encabezado': encabezado,
                'detalles': detalles,
                'total': total_asiento
            })

            asientos_agrupados[piscina]['subtotal'] += total_asiento
            total_general += total_asiento

        # Convertir a lista ordenada
        piscinas_ordenadas = sorted(asientos_agrupados.values(), key=lambda x: x['numero'])

        context['piscinas'] = piscinas_ordenadas
        context['total_general'] = total_general
        context['fecha_actual'] = datetime.now()

        return context


class DiagnosticoContableView(TemplateView):
    template_name = 'app_contabilidad_planCuentas/asientos_contables/diagnostico_contable.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Contar registros
        context['total_asientos'] = EncabezadoCuentasPlanCuenta.objects.count()
        context['total_detalles'] = DetalleCuentasPlanCuenta.objects.count()
        context['total_egresos'] = Producto_Stock.objects.filter(tipo='EGRESO').count()
        context['productos_con_cuenta'] = Total_Stock.objects.exclude(plan_cuenta__isnull=True).count()
        context['total_productos'] = Total_Stock.objects.count()
        context['piscinas_con_cuenta'] = Piscinas.objects.exclude(plan_cuenta__isnull=True).count()
        context['total_piscinas'] = Piscinas.objects.count()

        # Últimos asientos
        context['ultimos_asientos'] = EncabezadoCuentasPlanCuenta.objects.select_related('empresa').order_by('-id')[:5]

        # Últimos egresos
        context['ultimos_egresos'] = Producto_Stock.objects.filter(tipo='EGRESO').select_related(
            'producto_empresa__nombre_prod'
        ).order_by('-id')[:10]

        # Productos sin cuenta
        context['productos_sin_cuenta'] = Total_Stock.objects.filter(plan_cuenta__isnull=True).select_related(
            'nombre_prod', 'nombre_empresa')[:10]

        # Piscinas sin cuenta
        context['piscinas_sin_cuenta'] = Piscinas.objects.filter(plan_cuenta__isnull=True)[:10]

        return context


class ReportePiscinaInsumosView(TemplateView):
    template_name = 'app_contabilidad_planCuentas/asientos_contables/reporte_piscina_insumos.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Importar modelos
        from app_contabilidad_planCuentas.models import EncabezadoCuentasPlanCuenta, DetalleCuentasPlanCuenta
        from app_empresa.app_reg_empresa.models import Empresa

        # Filtros de fecha y empresa
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        empresa_id = self.request.GET.get('empresa')

        # Query base - solo asientos de stock/consumo
        query = Q(tip_transa='EGRESO') | Q(descripcion__icontains='Consumo')

        if fecha_desde:
            query &= Q(fecha__gte=fecha_desde)
        if fecha_hasta:
            query &= Q(fecha__lte=fecha_hasta)
        if empresa_id:
            query &= Q(empresa_id=empresa_id)

        # Obtener asientos con detalles
        asientos = EncabezadoCuentasPlanCuenta.objects.filter(query).select_related('empresa').prefetch_related(
            'detallecuentasplancuenta_set__cuenta'
        ).order_by('fecha', 'codigo')

        # Estructurar datos por piscina y producto
        piscinas_data = defaultdict(lambda: {'productos': defaultdict(list), 'total': Decimal('0')})

        for asiento in asientos:
            # Extraer número de piscina de la descripción
            piscina_num = self._extraer_numero_piscina(asiento.descripcion)
            if not piscina_num:
                continue

            # Obtener producto de la descripción
            producto_nombre = self._extraer_producto(asiento.descripcion)

            # Obtener detalles del asiento
            detalles = asiento.detallecuentasplancuenta_set.all()

            # Buscar el monto del DEBE (consumo en piscina)
            monto_debe = Decimal('0')
            for detalle in detalles:
                if detalle.debe and detalle.debe > 0:
                    monto_debe = detalle.debe
                    break

            if monto_debe > 0:
                # Agregar egreso al producto en la piscina
                piscinas_data[piscina_num]['productos'][producto_nombre].append({
                    'tipo': 'OE',
                    'documento': asiento.comprobante or asiento.codigo,
                    'fecha': asiento.fecha.strftime('%d/%m/%Y') if asiento.fecha else '',
                    'cantidad': monto_debe,
                    'precio': Decimal('0'),  # Se calculará si hay precio unitario
                    'total': monto_debe,
                })
                piscinas_data[piscina_num]['total'] += monto_debe

        # Convertir a lista ordenada
        piscinas_list = []
        total_general_cantidad = Decimal('0')
        total_general_monto = Decimal('0')

        for piscina_num in sorted(piscinas_data.keys()):
            productos_list = []
            total_piscina_cantidad = Decimal('0')
            total_piscina_monto = Decimal('0')

            for producto_nombre in sorted(piscinas_data[piscina_num]['productos'].keys()):
                egresos = piscinas_data[piscina_num]['productos'][producto_nombre]
                total_producto_cantidad = sum(e['cantidad'] for e in egresos)
                total_producto_monto = sum(e['total'] for e in egresos)

                # Calcular precio promedio si hay cantidad
                precio_promedio = total_producto_monto / total_producto_cantidad if total_producto_cantidad > 0 else Decimal(
                    '0')

                # Actualizar precio en cada egreso
                for egreso in egresos:
                    egreso['precio'] = precio_promedio

                productos_list.append({
                    'nombre': producto_nombre,
                    'egresos': egresos,
                    'total_cantidad': total_producto_cantidad,
                    'total_monto': total_producto_monto,
                })

                total_piscina_cantidad += total_producto_cantidad
                total_piscina_monto += total_producto_monto

            piscinas_list.append({
                'numero': piscina_num,
                'productos': productos_list,
                'total_cantidad': total_piscina_cantidad,
                'total_monto': total_piscina_monto,
            })

            total_general_cantidad += total_piscina_cantidad
            total_general_monto += total_piscina_monto

        # Obtener empresa para el encabezado
        empresa = None
        if empresa_id:
            try:
                empresa = Empresa.objects.get(pk=empresa_id)
            except Empresa.DoesNotExist:
                pass

        context['nombre'] = 'DETALLE PISCINA POR INSUMOS'
        context['empresa'] = empresa
        context['piscinas'] = piscinas_list
        context['total_general_cantidad'] = total_general_cantidad
        context['total_general_monto'] = total_general_monto
        context['fecha_desde'] = fecha_desde
        context['fecha_hasta'] = fecha_hasta
        context['empresas'] = Empresa.objects.all()

        return context

    def _extraer_numero_piscina(self, descripcion):
        """Extrae el número de piscina de la descripción"""
        import re
        if not descripcion:
            return None
        match = re.search(r'Piscina\s*(\d+)', descripcion, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    def _extraer_producto(self, descripcion):
        """Extrae el nombre del producto de la descripción"""
        if not descripcion:
            return "Producto desconocido"
        # La descripción típica es: "Consumo de PRODUCTO en Piscina X"
        import re
        match = re.search(r'Consumo de (.+?) en Piscina', descripcion, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return descripcion[:50]  # Usar los primeros 50 caracteres


class ConsumoPiscinaInsumosView(TemplateView):
    template_name = 'app_consumo_piscinas/consumo_piscina_insumo/consumo_piscina_insumos.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        empresa_id = self.request.GET.get('empresa')

        filtros = Q(tipo='EGRESO', activo=True)

        if fecha_desde:
            filtros &= Q(fecha_ingreso__gte=fecha_desde)
        if fecha_hasta:
            filtros &= Q(fecha_ingreso__lte=fecha_hasta)
        if empresa_id:
            filtros &= Q(producto_empresa__nombre_empresa_id=empresa_id)

        movimientos = (
            Producto_Stock.objects
            .filter(filtros)
            .select_related('producto_empresa__nombre_prod')
            .order_by('fecha_ingreso')
        )

        piscinas_data = defaultdict(lambda: {'productos': defaultdict(list)})

        for mov in movimientos:
            if not mov.piscinas:
                continue

            piscina = mov.piscinas
            producto = mov.producto_empresa.nombre_prod

            cantidad = Decimal(mov.cantidad_egreso or 0)
            precio = Decimal(getattr(producto, 'costo_aplicacion', 0) or 0)
            total = cantidad * precio

            piscinas_data[piscina]['productos'][producto.nombre].append({
                'tipo': 'OE',
                'documento': mov.numero_guia,
                'fecha': mov.fecha_ingreso.strftime('%d/%m/%Y'),
                'cantidad': cantidad,
                'precio': precio,
                'total': total,
            })

        piscinas_list = []
        total_general = Decimal('0')

        for piscina, data in piscinas_data.items():
            productos_list = []
            total_piscina = Decimal('0')

            for producto_nombre, egresos in data['productos'].items():
                total_cantidad = sum(e['cantidad'] for e in egresos)
                total_monto = sum(e['total'] for e in egresos)

                productos_list.append({
                    'nombre': producto_nombre,
                    'egresos': egresos,
                    'total_cantidad': total_cantidad,
                    'total_monto': total_monto,
                })

                total_piscina += total_monto

            piscinas_list.append({
                'numero': piscina,
                'productos': productos_list,
                'total_monto': total_piscina,
            })

            total_general += total_piscina

        empresa = Empresa.objects.filter(pk=empresa_id).first() if empresa_id else None

        context.update({
            'nombre': 'DETALLE PISCINA POR INSUMOS',
            'empresa': empresa,
            'piscinas': piscinas_list,
            'total_general_monto': total_general,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'empresas': Empresa.objects.all(),
        })

        return context
