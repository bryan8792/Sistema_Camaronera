import decimal
import json
from datetime import date
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import *
from app_empresa.app_reg_empresa.models import Empresa, Piscinas
from app_inventario.app_categoria.models import Producto
from app_proveedor.models import Proveedor
from app_stock.app_detalle_stock.forms import ProdStockForm, ProdStockTotalForm
from app_stock.app_detalle_stock.models import Producto_Stock, Total_Stock
from app_stock.app_detalle_stock.forms import PISCINAS_ESCOGER


# EMPRESA PRESQUERA SAN MIGUEL
class crearStockPSMDirectoView(CreateView):
    model = Producto_Stock
    form_class = ProdStockForm
    template_name = 'app_stock_directo/stock_dir_crear_psm.html'
    success_url = reverse_lazy('app_stock_directo:listar_stock_directo_psm')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos Aplicación Directa PSM'
        context['id_producto_empresa'] = self.kwargs['pk']
        producto = Total_Stock.objects.get(pk=self.kwargs['pk'])
        context['producto'] = producto

        unidad_aplicacion = producto.nombre_prod.unid_aplicacion
        print('LA APLICACION ES  ' + unidad_aplicacion)
        if unidad_aplicacion == 'GR':
            aplicacion = 1000
        elif unidad_aplicacion == 'KG':
            aplicacion = 2.2
        elif unidad_aplicacion == 'CA':
            aplicacion = 1
        elif unidad_aplicacion == 'LB':
            aplicacion = 55
        else:
            aplicacion = 1000

        # context['unidad_aplicacion'] = producto.nombre_prod.unid_aplicacion
        context['aplicacion'] = aplicacion
        context['peso_presentacion'] = producto.nombre_prod.peso_presentacion
        # context['nombre_presentacion'] = producto.nombre_prod.nombre
        # context['total'] = decimal.Decimal(aplicacion) * producto.nombre_prod.peso_presentacion
        return context


class editarStockPSMDirectoView(UpdateView):
    model = Producto_Stock
    form_class = ProdStockForm
    template_name = 'app_stock_directo/stock_dir_editar_psm.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Guardamos la piscina_id de donde viene el usuario para mantener el filtro
        self.piscina_origen = request.GET.get('piscina_id', None)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos Aplicación Directa PSM'
        producto = self.object.producto_empresa
        context['producto'] = producto

        unidad_aplicacion = producto.nombre_prod.unid_aplicacion
        if unidad_aplicacion == 'GR':
            aplicacion = 1000
        elif unidad_aplicacion == 'KG':
            aplicacion = 2.2
        elif unidad_aplicacion == 'LB':
            aplicacion = 55
        else:
            aplicacion = 1000

        context['aplicacion'] = aplicacion
        context['peso_presentacion'] = producto.nombre_prod.peso_presentacion

        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        print(f"[DEBUG] Antes de guardar: ID={obj.pk}, Producto Empresa={obj.producto_empresa}")
        obj.save()
        print(f"[DEBUG] Después de guardar: ID={obj.pk}, Producto Empresa={obj.producto_empresa}")
        return super().form_valid(form)

    def form_invalid(self, form):
        print(f"[DEBUG] Errores del formulario: {form.errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        # Si el usuario vino con piscina_id en GET, mantenemos ese filtro
        if self.piscina_origen:
            return reverse_lazy(
                'app_stock_directo:listarpsmunico_directo',
                kwargs={'pk': self.piscina_origen}
            )
        # Si no, usamos el filtro basado en el objeto editado
        piscina_id = self.object.producto_empresa.piscina_id
        return reverse_lazy('app_stock_directo:listarpsmunico_directo', kwargs={'pk': piscina_id})


class listarStockPSMDirectoView(ListView):
    model = Total_Stock
    template_name = 'app_stock_directo/stock_dir_listar_psm.html'

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
        context['nombre'] = 'Stock Productos Aplicación Directa PSM'
        context['sotck'] = Total_Stock.objects.all()
        context['balanceados'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='BALANCEADOS',
                                                            nombre_empresa__siglas='PSM')
        # context['insumos'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='INSUMOS', nombre_empresa__siglas='PSM')
        context['insumos'] = Total_Stock.objects.filter(nombre_empresa__siglas='PSM')
        return context


class listarStockUnicoPSMDirectoView(ListView):
    model = Producto_Stock
    template_name = 'app_stock_directo/app_control/stock_unico_directo_listar_psm.html'

    # def get_queryset(self):
    #     return Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'], activo__exact=True)
    #     # return Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],
    #     #                                      producto_empresa__nombre_empresa__siglas__icontains='PSM',
    #     #                                      activo__exact=True)

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
        context['nombre'] = 'Stock Productos Aplicación Directa PSM'
        return context


# EMPRESA BIO CASCAJAL
class crearStockBIODirectoView(CreateView):
    model = Producto_Stock
    form_class = ProdStockForm
    template_name = 'app_stock_directo/stock_dir_crear_bio.html'
    success_url = reverse_lazy('app_stock_directo:listar_stock_directo_bio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos Aplicación Directa BIO'
        context['id_producto_empresa'] = self.kwargs['pk']
        producto = Total_Stock.objects.get(pk=self.kwargs['pk'])
        context['producto'] = producto

        unidad_aplicacion = producto.nombre_prod.unid_aplicacion
        if unidad_aplicacion == 'GR':
            aplicacion = 1000
        elif unidad_aplicacion == 'KG':
            aplicacion = 2.2
        elif unidad_aplicacion == 'LB':
            aplicacion = 55
        else:
            aplicacion = 1000

        context['aplicacion'] = aplicacion
        context['peso_presentacion'] = producto.nombre_prod.peso_presentacion

        return context


class editarStockBIODirectoView(UpdateView):
    model = Producto_Stock
    form_class = ProdStockForm
    template_name = 'app_stock_directo/stock_dir_editar_bio.html'
    success_url = reverse_lazy('app_stock_directo:listar_stock_directo_bio')

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Stock Productos Aplicación Directa BIO'
        producto = self.object.producto_empresa
        context['producto'] = producto

        unidad_aplicacion = producto.nombre_prod.unid_aplicacion
        if unidad_aplicacion == 'GR':
            aplicacion = 1000
        elif unidad_aplicacion == 'KG':
            aplicacion = 2.2
        elif unidad_aplicacion == 'LB':
            aplicacion = 55
        else:
            aplicacion = 1000

        context['aplicacion'] = aplicacion
        context['peso_presentacion'] = producto.nombre_prod.peso_presentacion

        return context


class listarStockBIODirectoView(ListView):
    model = Total_Stock
    template_name = 'app_stock_directo/stock_dir_listar_bio.html'

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
        context['nombre'] = 'Stock Productos Aplicación Directa BIO'
        context['sotck'] = Total_Stock.objects.all()
        context['balanceados'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='BALANCEADOS',
                                                            nombre_empresa__siglas='BIO')
        context['insumos'] = Total_Stock.objects.filter(nombre_prod__categoria__nombre__icontains='INSUMOS',
                                                        nombre_empresa__siglas='BIO')
        return context


class listarStockUnicoBIODirectoView(ListView):
    model = Producto_Stock
    template_name = 'app_stock_directo/app_control/stock_unico_listar_bio.html'

    def get_queryset(self):
        return Producto_Stock.objects.filter(producto_empresa_id=self.kwargs['pk'],
                                             producto_empresa__nombre_empresa__siglas__icontains='BIO',
                                             activo__exact=True)

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
        context['nombre'] = 'Stock Productos Aplicación Directa BIO'
        return context


class IngresoBodegaBalanceadoView(TemplateView):
    template_name = 'app_stock_directo/ingreso_bodega_balanceado.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Ingreso de Bodega Balanceado'

        # Obtener el siguiente número de documento INCREMENTAL
        ultimo_ingreso = Producto_Stock.objects.filter(
            numero_guia__icontains='INGRESO BODEGA'
        ).order_by('-id').first()

        if ultimo_ingreso and ultimo_ingreso.numero_guia:
            try:
                # Extraer el número del formato "ING-000001 INGRESO BODEGA"
                partes = ultimo_ingreso.numero_guia.split(' ')[0]  # "ING-000001"
                numero_str = partes.split('-')[1] if '-' in partes else '0'
                ultimo_num = int(numero_str)
                siguiente_num = ultimo_num + 1
            except (IndexError, ValueError):
                siguiente_num = 1
        else:
            siguiente_num = 1

        context['numero_documento'] = f"{siguiente_num:06d}"
        context['fecha_actual'] = date.today().strftime('%Y-%m-%d')

        # Obtener empresas para el dropdown
        context['empresas'] = Empresa.objects.all().order_by('nombre')

        # Obtener proveedores/bodegas - CORREGIDO: usar nombre_com en lugar de nombre
        context['proveedores'] = Proveedor.objects.all().order_by('nombre_com')

        return context

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        data = {'success': False}
        try:
            # Verificar si es petición AJAX para obtener productos por empresa
            body = json.loads(request.body)
            action = body.get('action', '')

            if action == 'get_productos_by_empresa':
                # Obtener productos filtrados por empresa
                empresa_id = body.get('empresa_id')

                if empresa_id:
                    productos = Total_Stock.objects.filter(
                        nombre_empresa_id=empresa_id
                    ).select_related('nombre_prod').order_by('nombre_prod__nombre')

                    productos_list = []
                    for prod in productos:
                        productos_list.append({
                            'id': prod.id,
                            'nombre': prod.nombre_prod.nombre if prod.nombre_prod else 'Sin nombre',
                            'peso': float(
                                prod.nombre_prod.peso_presentacion) if prod.nombre_prod and prod.nombre_prod.peso_presentacion else 0,
                        })

                    data['success'] = True
                    data['productos'] = productos_list
                else:
                    data['error'] = 'Debe seleccionar una empresa'

                return JsonResponse(data)

            # Guardar ingreso
            numero_documento = body.get('numero_documento')
            fecha = body.get('fecha')
            proveedor_id = body.get('proveedor_id')
            empresa_id = body.get('empresa_id')
            items = body.get('items', [])
            responsable = body.get('responsable', '')

            # Validar
            if not empresa_id:
                data['error'] = 'Debe seleccionar una empresa'
                return JsonResponse(data)

            if not items:
                data['error'] = 'Debe agregar al menos un producto'
                return JsonResponse(data)

            # Guardar cada item
            for item in items:
                producto_id = item.get('producto_id')
                cantidad_sacos = item.get('cantidad_sacos', 0)
                libras = item.get('libras', 0)
                total_libras = item.get('total_libras', 0)

                if producto_id and total_libras > 0:
                    # Obtener el producto (Total_Stock)
                    producto_stock = Total_Stock.objects.get(pk=producto_id)

                    # Crear el registro de ingreso
                    Producto_Stock.objects.create(
                        producto_empresa=producto_stock,
                        tipo='INGRESO',
                        cantidad_usar=cantidad_sacos,
                        cantidad_ingreso=total_libras,
                        cantidad_egreso=0,
                        fecha_ingreso=fecha,
                        numero_guia=f"ING-{numero_documento} INGRESO BODEGA",
                        responsable_ingreso=responsable,
                        piscinas='Todas las Piscinas',
                        activo=True,
                    )

            data['success'] = True
            data['message'] = 'Ingreso registrado correctamente'

        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data)


class EgresoBodegaBalanceadoView(TemplateView):
    template_name = 'app_stock_directo/egreso_bodega_balanceado.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Egreso de Bodega Balanceado'

        # Obtener el siguiente número de documento INCREMENTAL para EGRESO
        ultimo_egreso = Producto_Stock.objects.filter(
            numero_guia__icontains='EGRESO BODEGA'
        ).order_by('-id').first()

        if ultimo_egreso and ultimo_egreso.numero_guia:
            try:
                # Extraer el número del formato "EGR-000001 EGRESO BODEGA"
                partes = ultimo_egreso.numero_guia.split(' ')[0]  # "EGR-000001"
                numero_str = partes.split('-')[1] if '-' in partes else '0'
                ultimo_num = int(numero_str)
                siguiente_num = ultimo_num + 1
            except (IndexError, ValueError):
                siguiente_num = 1
        else:
            siguiente_num = 1

        context['numero_documento'] = f"{siguiente_num:06d}"
        context['fecha_actual'] = date.today().strftime('%Y-%m-%d')

        # Obtener empresas para el dropdown
        context['empresas'] = Empresa.objects.all().order_by('nombre')

        # Obtener proveedores/bodegas
        context['proveedores'] = Proveedor.objects.all().order_by('nombre_com')

        return context

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        data = {'success': False}
        try:
            # Verificar si es petición AJAX para obtener productos por empresa
            body = json.loads(request.body)
            action = body.get('action', '')

            if action == 'get_productos_by_empresa':
                # Obtener productos filtrados por empresa
                empresa_id = body.get('empresa_id')

                if empresa_id:
                    productos = Total_Stock.objects.filter(
                        nombre_empresa_id=empresa_id
                    ).select_related('nombre_prod').order_by('nombre_prod__nombre')

                    productos_list = []
                    for prod in productos:
                        productos_list.append({
                            'id': prod.id,
                            'nombre': prod.nombre_prod.nombre if prod.nombre_prod else 'Sin nombre',
                            'peso': float(
                                prod.nombre_prod.peso_presentacion) if prod.nombre_prod and prod.nombre_prod.peso_presentacion else 0,
                        })

                    data['success'] = True
                    data['productos'] = productos_list
                else:
                    data['error'] = 'Debe seleccionar una empresa'

                return JsonResponse(data)

            # Guardar egreso
            numero_documento = body.get('numero_documento')
            fecha = body.get('fecha')
            proveedor_id = body.get('proveedor_id')
            empresa_id = body.get('empresa_id')
            items = body.get('items', [])
            responsable = body.get('responsable', '')

            # Validar
            if not empresa_id:
                data['error'] = 'Debe seleccionar una empresa'
                return JsonResponse(data)

            if not items:
                data['error'] = 'Debe agregar al menos un producto'
                return JsonResponse(data)

            # Guardar cada item
            for item in items:
                producto_id = item.get('producto_id')
                cantidad_sacos = item.get('cantidad_sacos', 0)
                libras = item.get('libras', 0)
                total_libras = item.get('total_libras', 0)

                if producto_id and total_libras > 0:
                    # Obtener el producto (Total_Stock)
                    producto_stock = Total_Stock.objects.get(pk=producto_id)

                    # Crear el registro de egreso
                    Producto_Stock.objects.create(
                        producto_empresa=producto_stock,
                        tipo='EGRESO',
                        cantidad_usar=cantidad_sacos,
                        cantidad_ingreso=0,
                        cantidad_egreso=total_libras,
                        fecha_ingreso=fecha,
                        numero_guia=f"EGR-{numero_documento} EGRESO BODEGA",
                        responsable_ingreso=responsable,
                        piscinas='Todas las Piscinas',
                        activo=True,
                    )

            data['success'] = True
            data['message'] = 'Egreso registrado correctamente'

        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data)



class crearEgresoDirectoMatrizView(TemplateView):
    template_name = 'app_stock_directo/egreso_directo_matriz.html'
    success_url = reverse_lazy('app_detalle_stock:listar_stock_directo_psm')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']

            # -------- PASO 1: cargar piscinas + productos de la empresa --------
            if action == 'search_matriz':

                empresa = request.POST.get('empresa')
                piscinas = []
                qs_piscinas = Piscinas.objects.filter(
                    empresa__siglas=empresa,
                    estado=True,
                    pis=True
                ).order_by('numero')
                for p in qs_piscinas:
                    piscinas.append({
                        'valor': p.id,  # ID de la piscina
                        'label': p.numero,  # Nombre mostrado en la cabecera
                    })

                productos = []

                qs_prod = Total_Stock.objects.filter(
                    nombre_empresa__siglas=empresa
                ).order_by('nombre_prod__nombre')

                for ts in qs_prod:
                    productos.append({
                        'id': ts.id,
                        'nombre': ts.nombre_prod.nombre,
                        'stock': format(ts.stock, '.2f'),
                    })

                data['piscinas'] = piscinas
                data['productos'] = productos

            # -------- GUARDAR: un egreso por celda con cantidad > 0 --------
            elif action == 'create':
                with transaction.atomic():
                    empresa = request.POST.get('empresa')
                    fecha = request.POST.get('fecha') or date.today().strftime('%Y-%m-%d')
                    responsable = request.POST.get('responsable', '')
                    guia = request.POST.get('numero_guia') or ('EGRESO PISCINAS - %s' % empresa)
                    items = json.loads(request.POST.get('items', '[]'))

                    registros = 0
                    for i in items:
                        cantidad = decimal.Decimal(str(i.get('cantidad') or '0'))
                        if cantidad <= 0:
                            continue

                        total_stock = Total_Stock.objects.get(pk=int(i['producto']))

                        reg = Producto_Stock()
                        reg.producto_empresa = total_stock
                        reg.tipo = 'EGRESO'
                        piscina_id = i.get('piscina')
                        try:
                            piscina = Piscinas.objects.get(pk=piscina_id)
                            reg.piscinas = piscina.numero
                        except:
                            reg.piscinas = 'Sin Piscina'
                        reg.cantidad_usar = cantidad
                        reg.cantidad_egreso = cantidad
                        reg.cantidad_ingreso = decimal.Decimal('0')
                        reg.fecha_ingreso = fecha
                        reg.numero_guia = guia
                        reg.responsable_ingreso = responsable
                        reg.activo = True
                        reg.save()  # save() descuenta el stock automaticamente
                        registros += 1

                    if registros == 0:
                        data['error'] = 'No ingreso ninguna cantidad para registrar.'
                    else:
                        data['success'] = True
                        data['registros'] = registros

            else:
                data['error'] = 'Ha ocurrido un error'

        except Exception as e:
            data['error'] = 'El error es: ' + str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Productos Aplicacion Directa'
        context['entity'] = 'Egreso a Piscinas'
        context['list_url'] = self.success_url
        context['action'] = 'create'
        context['empresas'] = Empresa.objects.all().order_by('siglas')
        context['fecha'] = date.today().strftime('%Y-%m-%d')
        return context
