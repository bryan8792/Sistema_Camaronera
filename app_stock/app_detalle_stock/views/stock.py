
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView
from django.utils import timezone
from datetime import datetime
from app_contabilidad_planCuentas.models import PlanCuenta, DetalleCuentasPlanCuenta, EncabezadoCuentasPlanCuenta
from app_dieta.app_dieta_reg.models import DetalleDiaDieta
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


@receiver(post_save, sender=Producto_Stock)
def crear_asiento_contable_egreso(sender, instance, created, **kwargs):
    """
    Signal que crea automáticamente asientos contables cuando hay un EGRESO de stock
    """

    if not created or instance.tipo != 'EGRESO':
        return

    print(f"\n{'=' * 60}")
    print(f"[CONTABILIDAD] INICIANDO PROCESO DE ASIENTO CONTABLE")
    print(f"{'=' * 60}")

    try:
        print(f"[CONTABILIDAD] ID Producto_Stock: {instance.id}")
        print(f"[CONTABILIDAD] Tipo: {instance.tipo}")
        print(f"[CONTABILIDAD] Cantidad egreso: {instance.cantidad_egreso}")

        piscina_obj = instance.piscinas
        if not piscina_obj:
            print(f"[CONTABILIDAD] ERROR: No hay piscina asignada")
            return

        piscina_nombre = str(piscina_obj)
        print(f"[CONTABILIDAD] Piscina: {piscina_nombre}")

        match = re.search(r'\d+', piscina_nombre)
        if not match:
            print(f"[CONTABILIDAD] ERROR: No se pudo extraer número de piscina")
            return

        piscina_numero = int(match.group())
        print(f"[CONTABILIDAD] Piscina número: {piscina_numero}")

        empresa_siglas = 'PSM' if 1 <= piscina_numero <= 20 else 'BIO' if 21 <= piscina_numero <= 45 else None
        if not empresa_siglas:
            print(f"[CONTABILIDAD] ERROR: Piscina fuera de rango")
            return

        print(f"[CONTABILIDAD] Empresa: {empresa_siglas}")

        print(f"[CONTABILIDAD] Buscando empresa...")
        try:
            empresa_obj = Empresa.objects.filter(siglas=empresa_siglas).first()
            print(f"[CONTABILIDAD] Empresa query ejecutada: {empresa_obj}")
        except Exception as e:
            print(f"[CONTABILIDAD] ERROR en query Empresa: {e}")
            return

        if not empresa_obj:
            print(f"[CONTABILIDAD] ERROR: Empresa no encontrada")
            return

        print(f"[CONTABILIDAD] Empresa OK: {empresa_obj.nombre}")

        print(f"[CONTABILIDAD] Buscando producto...")
        try:
            producto_id = instance.producto_empresa.nombre_prod.id
            print(f"[CONTABILIDAD] Producto ID: {producto_id}")
        except Exception as e:
            print(f"[CONTABILIDAD] ERROR accediendo a producto: {e}")
            import traceback
            traceback.print_exc()
            return

        print(f"[CONTABILIDAD] Buscando Total_Stock...")
        try:
            stock_total = Total_Stock.objects.filter(
                nombre_prod__id=producto_id,
                nombre_empresa__id=empresa_obj.id
            ).first()
            print(f"[CONTABILIDAD] Total_Stock: {stock_total}")
        except Exception as e:
            print(f"[CONTABILIDAD] ERROR en query Total_Stock: {e}")
            import traceback
            traceback.print_exc()
            return

        if not stock_total or not stock_total.plan_cuenta:
            print(f"[CONTABILIDAD] ERROR: Producto sin plan de cuentas")
            return

        cuenta_producto = stock_total.plan_cuenta
        print(f"[CONTABILIDAD] Cuenta producto: {cuenta_producto.codigo}")

        print(f"[CONTABILIDAD] Buscando cuenta SUMINISTROS...")
        cuenta_suministros = None

        if hasattr(piscina_obj, 'cuenta_suministros') and piscina_obj.cuenta_suministros:
            cuenta_suministros = piscina_obj.cuenta_suministros
            print(f"[CONTABILIDAD] Cuenta SUMINISTROS (FK): {cuenta_suministros.codigo}")
        else:
            # Buscar por nombre
            cuenta_piscina = None
            for formato in [f'PISCINA#{piscina_numero}', f'PISCINA# {piscina_numero}']:
                cuenta_piscina = PlanCuenta.objects.filter(
                    empresa=empresa_obj,
                    nombre__icontains=formato,
                    estado=True
                ).first()
                if cuenta_piscina:
                    break

            if not cuenta_piscina:
                print(f"[CONTABILIDAD] ERROR: No existe cuenta piscina")
                return

            cuenta_suministros = PlanCuenta.objects.filter(
                empresa=empresa_obj,
                parentId=cuenta_piscina,
                nombre__iexact='SUMINISTROS',
                estado=True
            ).first()

            if not cuenta_suministros:
                print(f"[CONTABILIDAD] ERROR: No existe subcuenta SUMINISTROS")
                return

        print(f"[CONTABILIDAD] Cuenta SUMINISTROS: {cuenta_suministros.codigo}")

        monto = float(instance.cantidad_egreso or 0)
        if monto <= 0:
            print(f"[CONTABILIDAD] ERROR: Monto inválido")
            return

        print(f"[CONTABILIDAD] Monto: ${monto:.2f}")

        print(f"[CONTABILIDAD] Creando encabezado...")
        encabezado = EncabezadoCuentasPlanCuenta.objects.create(
            codigo=int(datetime.now().timestamp()),
            tip_cuenta='EGRESO DE INVENTARIO',
            tip_transa='EGRESO',
            fecha=instance.fecha_ingreso or timezone.now().date(),
            comprobante=f"EGR-{instance.id}-P{piscina_numero}",
            descripcion=f"Consumo en Piscina {piscina_numero}",
            empresa=empresa_obj,
            reg_control='RT'
        )
        print(f"[CONTABILIDAD] Encabezado creado ID: {encabezado.id}")

        detalle_debe = DetalleCuentasPlanCuenta.objects.create(
            encabezadocuentaplan=encabezado,
            orden=1,
            cuenta=cuenta_suministros,
            detalle=f"Consumo P#{piscina_numero}",
            debe=monto,
            haber=0.00,
            origen='STOCK'
        )
        print(f"[CONTABILIDAD] DEBE creado ID: {detalle_debe.id} - ${monto} - ${detalle_debe.orden}")

        detalle_haber = DetalleCuentasPlanCuenta.objects.create(
            encabezadocuentaplan=encabezado,
            orden=2,
            cuenta=cuenta_producto,
            detalle=f"Egreso inventario",
            debe=0.00,
            haber=monto,
            origen='STOCK'
        )
        print(f"[CONTABILIDAD] HABER creado ID: {detalle_haber.id} - ${monto}")

        print(f"{'=' * 60}")
        print(f"[CONTABILIDAD] ASIENTO CONTABLE CREADO EXITOSAMENTE")
        print(f"[CONTABILIDAD] Comprobante: {encabezado.comprobante}")
        print(f"{'=' * 60}\n")

    except Exception as e:
        print(f"{'=' * 60}")
        print(f"[CONTABILIDAD] ERROR CRITICO EN SIGNAL")
        print(f"[CONTABILIDAD] Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'=' * 60}\n")


def connect_signals():
    """
    Connect all signals - call this in apps.py ready() method
    """
    pass



