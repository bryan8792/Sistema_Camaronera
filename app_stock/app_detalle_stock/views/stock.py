
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
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
class CrearStockConCuentaView(CreateView):
    model = Total_Stock
    form_class = StockAccountingForm
    template_name = 'app_stock/stock_crear_con_cuenta.html'
    success_url = reverse_lazy('app_stock:listar_stock_bio')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        empresa_id = self.kwargs.get('empresa_id')
        print("empresa_id:", empresa_id)

        if empresa_id:
            try:
                empresa = Empresa.objects.get(pk=empresa_id)

                # Prellenar el campo empresa
                kwargs.setdefault('initial', {})
                kwargs['initial']['nombre_empresa'] = empresa

                # Pasar empresa al formulario
                kwargs['empresa_obj'] = empresa

            except Empresa.DoesNotExist:
                pass

        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.object.plan_cuenta:
            self.object.cod_contable = self.object.plan_cuenta.codigo
            self.object.save(update_fields=['cod_contable'])

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_id = self.kwargs.get('empresa_id')

        if empresa_id:
            context['empresa'] = Empresa.objects.get(pk=empresa_id)
            context['plan_cuentas'] = PlanCuenta.objects.filter(
                empresa_id=empresa_id,
                estado=True
            ).order_by('codigo')

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


def crear_asiento_contable_egreso(sender, instance, created, **kwargs):
    """
    Signal that automatically creates accounting entries when stock is withdrawn
    Now automatically determines company from piscina number (1-20=PSM, 21-45=BIO)
    """

    # Only process EGRESO (withdrawal) movements
    if instance.tipo_movimiento != 'EGRESO':
        return

    try:
        piscina_numero = None
        if hasattr(instance.piscina, 'nombre'):
            piscina_numero = instance.piscina.nombre
        elif hasattr(instance.piscina, 'numero'):
            piscina_numero = instance.piscina.numero

        empresa_detectada = get_empresa_from_piscina(piscina_numero)

        if not empresa_detectada:
            print(f"[CONTABILIDAD] No se pudo detectar empresa para piscina {piscina_numero}")
            return

        # Get related stock record with detected company
        stock_total = Total_Stock.objects.get(
            nombre_prod=instance.producto,
            nombre_empresa__nombre=empresa_detectada
        )

        # Verify that the product has an accounting plan assigned
        if not stock_total.plan_cuenta:
            print(f"[CONTABILIDAD] Producto {instance.producto.nombre} sin plan de cuentas para {empresa_detectada}")
            return

        # Get company object
        empresa = stock_total.nombre_empresa

        # Create accounting header (encabezado)
        encabezado = EncabezadoCuentasPlanCuenta.objects.create(
            codigo=int(datetime.now().timestamp()),
            tip_cuenta='EGRESO DE INVENTARIO',
            tip_transa='EGRESO',
            fecha=instance.fecha or timezone.now().date(),
            comprobante=f"EGR-{instance.id}",
            descripcion=f"Egreso de {instance.producto.nombre} en {piscina_numero} ({empresa_detectada})",
            empresa=empresa,
            reg_control='RT'
        )

        # Create detail entries (detalles)
        # Entry 1: Debit from inventory (inventario)
        cuenta_inventario = stock_total.plan_cuenta

        DetalleCuentasPlanCuenta.objects.create(
            encabezadocuentaplan=encabezado,
            orden=1,
            cuenta=cuenta_inventario,
            detalle=f"Egreso: {instance.producto.nombre}",
            debe=float(instance.cantidad),
            haber=0.00,
            origen='STOCK'
        )

        # Entry 2: Credit to expense account (gasto)
        try:
            # Look for an expense account related to the product
            cuenta_gasto = PlanCuenta.objects.filter(
                empresa=empresa,
                nombre__icontains=instance.producto.categoria.nombre.split()[0],
                tipo_cuenta='GASTO',
                estado=True
            ).first()

            if cuenta_gasto:
                DetalleCuentasPlanCuenta.objects.create(
                    encabezadocuentaplan=encabezado,
                    orden=2,
                    cuenta=cuenta_gasto,
                    detalle=f"Gasto: {instance.producto.nombre}",
                    debe=0.00,
                    haber=float(instance.cantidad),
                    origen='STOCK'
                )
        except Exception as e:
            print(f"[CONTABILIDAD] Error creando entrada de gasto: {str(e)}")

        # Save the accounting code to stock_prod for reference
        instance.cod_contable = stock_total.plan_cuenta.codigo
        instance.save(update_fields=['cod_contable'])

        print(f"[CONTABILIDAD] Asiento contable creado para egreso ID {instance.id} - Empresa: {empresa_detectada}")

    except Total_Stock.DoesNotExist:
        print(f"[CONTABILIDAD] Stock total no encontrado para {instance.producto} en empresa detectada")
    except Exception as e:
        print(f"[CONTABILIDAD] Error al crear asiento contable: {str(e)}")


def connect_signals():
    """
    Connect all signals - call this in apps.py ready() method
    """
    pass

