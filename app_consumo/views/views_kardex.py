from collections import defaultdict

from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, DecimalField
from django.db.models.functions import Coalesce
from datetime import datetime
import json
from app_empresa.app_reg_empresa.models import Empresa, Piscinas
from app_stock.app_detalle_stock.models import Producto_Stock


class KardexBodegaView(TemplateView):
    """
    Vista para generar el Kardex de Bodega de Insumos
    Muestra: Stock PSM, Stock BIO, Stock Total, Consumo por Empresa
    """
    template_name = 'app_consumo/kardex_bodega.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            action = request.POST.get('action', '')

            if action == 'get_kardex_data':
                return self._get_kardex_data(request)
            elif action == 'get_consumo_piscinas':
                return self._get_consumo_piscinas(request)
            else:
                return JsonResponse({'error': 'Action no válida'}, safe=False)

        except Exception as e:
            print(f"Error en kardex: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, safe=False)

    def _get_kardex_data(self, request):
        """Obtiene datos consolidados del kardex"""
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')

        productos_dict = {}

        query = Producto_Stock.objects.filter(
            tipo='EGRESO',
            activo=True
        ).select_related('producto_empresa', 'producto_empresa__nombre_prod',
                         'producto_empresa__nombre_empresa')

        if start_date and end_date:
            query = query.filter(fecha_ingreso__range=[start_date, end_date])

        for item in query:
            try:
                prod_id = item.producto_empresa.id
                prod_name = item.producto_empresa.nombre_prod.nombre

                if prod_id not in productos_dict:
                    productos_dict[prod_id] = {
                        'id': prod_id,
                        'nombre_producto': prod_name,
                        'presentacion': item.producto_empresa.nombre_prod.presentacion or '-',
                        'unidad': item.producto_empresa.nombre_prod.presentacion or '-',
                        'stock_psm': 0.0,
                        'stock_bio': 0.0,
                        'stock_total': float(item.producto_empresa.stock),
                        'consumo_total': 0.0,
                    }

                # Determinar si es PSM o BIO según el nombre de empresa
                empresa_sigla = item.producto_empresa.nombre_empresa.siglas
                cantidad = float(item.cantidad_egreso)

                if 'PSM' in empresa_sigla.upper() or 'SAN MIGUEL' in empresa_sigla.upper():
                    productos_dict[prod_id]['stock_psm'] += cantidad
                elif 'BIO' in empresa_sigla.upper() or 'CASCAJAL' in empresa_sigla.upper():
                    productos_dict[prod_id]['stock_bio'] += cantidad

                productos_dict[prod_id]['consumo_total'] += cantidad
            except Exception as e:
                print(f"Error procesando item {item.id}: {str(e)}")
                continue

        data = list(productos_dict.values())
        return JsonResponse(data, safe=False)

    def _get_consumo_piscinas(self, request):
        """Detalle de consumo por piscinas y empresas"""
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')

        query = Producto_Stock.objects.filter(
            tipo='EGRESO',
            activo=True
        ).select_related('producto_empresa', 'producto_empresa__nombre_prod',
                         'producto_empresa__nombre_empresa')

        if start_date and end_date:
            query = query.filter(fecha_ingreso__range=[start_date, end_date])

        data = []
        for item in query:
            try:
                data.append({
                    'id': item.id,
                    'empresa': item.producto_empresa.nombre_empresa.siglas or 'N/A',
                    'piscina': item.piscinas or 'Todas',
                    'fecha': item.fecha_ingreso.strftime('%Y-%m-%d') if item.fecha_ingreso else '',
                    'producto': item.producto_empresa.nombre_prod.nombre,
                    'cantidad': float(item.cantidad_egreso),
                    'unidad': item.producto_empresa.nombre_prod.presentacion or '-',
                    'responsable': item.responsable_ingreso or '-',
                    'numero_guia': item.numero_guia or '-',
                    'observacion': item.observacion or 'Sin Novedades',
                })
            except Exception as e:
                print(f"Error procesando item {item.id}: {str(e)}")
                continue

        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'KARDEX BODEGA DE INSUMOS'
        context['empresas'] = Empresa.objects.all()
        return context


# class KardexBodegaGeneralView(TemplateView):
#     """
#     Vista para generar el Kardex de Bodega de Insumos
#     Muestra: Stock PSM, Stock BIO, Stock Total, Consumo por Empresa
#     """
#     template_name = 'app_consumo/kardex_bodega_general.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         try:
#             action = request.POST.get('action', '')
#
#             if action == 'get_kardex_horizontal':
#                 return self._get_kardex_horizontal(request)
#             else:
#                 return JsonResponse({'error': 'Action no válida'}, safe=False)
#
#         except Exception as e:
#             print(f"Error en kardex: {str(e)}")
#             return JsonResponse({'error': str(e)}, safe=False)
#
#     def _get_kardex_horizontal(self, request):
#         """
#         Obtiene datos agrupados para la tabla horizontal:
#         FECHA – EMPRESA – PRODUCTOS (ING, EGR, STOCK)
#         """
#         start_date = request.POST.get('start_date', '')
#         end_date = request.POST.get('end_date', '')
#
#         # Consulta principal
#         query = Producto_Stock.objects.filter(activo=True).select_related(
#             'producto_empresa',
#             'producto_empresa__nombre_prod',
#             'producto_empresa__nombre_empresa'
#         ).order_by('fecha_ingreso')
#
#         if start_date and end_date:
#             query = query.filter(fecha_ingreso__range=[start_date, end_date])
#
#         datos_agrupados = {}
#         todas_productos = set()
#
#         for item in query:
#             try:
#                 fecha = item.fecha_ingreso.strftime('%d-%m-%Y') if item.fecha_ingreso else 'Sin fecha'
#                 empresa = item.producto_empresa.nombre_empresa.siglas or 'N/A'
#                 producto_nombre = item.producto_empresa.nombre_prod.nombre
#
#                 clave = f"{fecha}_{empresa}"
#
#                 # Crear fila si no existe
#                 if clave not in datos_agrupados:
#                     datos_agrupados[clave] = {
#                         'fecha': fecha,
#                         'empresa': empresa,
#                         'productos': {}
#                     }
#
#                 # Crear producto si no existe
#                 if producto_nombre not in datos_agrupados[clave]['productos']:
#                     datos_agrupados[clave]['productos'][producto_nombre] = {
#                         'ingreso': 0.0,
#                         'egreso': 0.0,
#                         'stock': float(item.producto_empresa.stock or 0),
#                         'unidad': item.producto_empresa.nombre_prod.presentacion or '-'
#                     }
#
#                 # Asignar datos
#                 if item.tipo == 'INGRESO':
#                     datos_agrupados[clave]['productos'][producto_nombre]['ingreso'] += float(item.cantidad_ingreso or 0)
#                 else:
#                     datos_agrupados[clave]['productos'][producto_nombre]['egreso'] += float(item.cantidad_egreso or 0)
#
#                 todas_productos.add(producto_nombre)
#
#             except Exception as e:
#                 print(f"Error procesando item {item.id}: {str(e)}")
#                 continue
#
#         productos_ordenados = sorted(todas_productos)
#
#         resultado = []
#         for clave in sorted(datos_agrupados.keys()):
#             fila = datos_agrupados[clave]
#             fila['productos_sorted'] = productos_ordenados
#             resultado.append(fila)
#
#         return JsonResponse({
#             'datos': resultado,
#             'productos': productos_ordenados,
#             'total_fechas': len(set([d['fecha'] for d in resultado]))
#         }, safe=False)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['titulo'] = 'KARDEX BODEGA DE INSUMOS'
#         context['empresas'] = Empresa.objects.all()
#         return context


class KardexBodegaGeneralView(TemplateView):
    template_name = 'app_consumo/kardex_bodega_general.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            action = request.POST.get('action', '')
            if action == 'get_kardex_horizontal':
                return self._get_kardex_horizontal(request)
            else:
                return JsonResponse({'error': f'Action no válida: {action}'}, safe=False)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, safe=False)

    def _get_kardex_horizontal(self, request):
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        empresa_filter = request.POST.get('empresa', '')
        piscina_filter = request.POST.get('piscina', '')

        qs = Producto_Stock.objects.filter(activo=True).select_related(
            'producto_empresa',
            'producto_empresa__nombre_prod',
            'producto_empresa__nombre_prod__categoria',
            'producto_empresa__nombre_empresa'
        ).order_by('fecha_ingreso', 'producto_empresa__nombre_prod__nombre')

        if start_date and end_date:
            qs = qs.filter(fecha_ingreso__range=[start_date, end_date])

        if empresa_filter:
            try:
                eid = int(empresa_filter)
                qs = qs.filter(producto_empresa__nombre_empresa__id=eid)
            except Exception:
                qs = qs.filter(producto_empresa__nombre_empresa__siglas__iexact=empresa_filter)

        # FILTRO DE PISCINA: por ID o por orden
        if piscina_filter:
            try:
                try:
                    # Intentamos como ID
                    pid = int(piscina_filter)
                    piscina_obj = Piscinas.objects.get(id=pid)
                except ValueError:
                    # Si no es número, lo buscamos por orden
                    piscina_obj = Piscinas.objects.get(orden__iexact=piscina_filter.strip())

                qs = qs.filter(piscinas=piscina_obj)
            except Piscinas.DoesNotExist:
                print(f"[KARDEX DEBUG] Piscina no encontrada: {piscina_filter}")
                qs = qs.none()

        # Diccionarios para almacenar los consumos
        datos_balanceados = defaultdict(lambda: defaultdict(float))
        datos_insumos_balanceado = defaultdict(lambda: defaultdict(float))
        datos_campo = defaultdict(lambda: defaultdict(float))

        productos_balanceados = set()
        productos_insumos_balanceado = set()
        productos_campo = set()
        fechas_set = set()

        for item in qs:
            if item.tipo != 'EGRESO':
                continue

            fecha = item.fecha_ingreso.strftime('%Y-%m-%d')
            consumo = float(item.cantidad_egreso or 0)
            if consumo <= 0:
                continue

            producto_obj = item.producto_empresa.nombre_prod
            producto_nombre = str(producto_obj)

            categoria_id = getattr(producto_obj.categoria, 'id', None)
            aplicacion_directa = getattr(producto_obj, 'aplic_directa', False)

            # Solo agregamos si tiene valor
            if categoria_id == 2 and consumo > 0:
                datos_balanceados[fecha][producto_nombre] += consumo
                productos_balanceados.add(producto_nombre)
            elif aplicacion_directa and consumo > 0:
                datos_campo[fecha][producto_nombre] += consumo
                productos_campo.add(producto_nombre)
            elif categoria_id == 1 and consumo > 0:
                datos_insumos_balanceado[fecha][producto_nombre] += consumo
                productos_insumos_balanceado.add(producto_nombre)

            fechas_set.add(fecha)

        fechas = sorted(fechas_set)

        # Construye lista de filas solo con fecha y valores existentes
        def construir_lista(productos, datos):
            lista = []
            for f in fechas:
                fila = {'fecha': f, 'productos': {}}
                for p in productos:
                    valor = datos[f].get(p)
                    if valor:  # Solo agrega si hay valor
                        fila['productos'][p] = valor
                if fila['productos']:  # Solo agrega fila si hay datos
                    lista.append(fila)
            return lista

        response_data = {
            'status': 'ok',
            'productos_balanceados': sorted(productos_balanceados),
            'datos_balanceados': construir_lista(sorted(productos_balanceados), datos_balanceados),
            'productos_insumos': sorted(productos_insumos_balanceado),
            'datos_insumos': construir_lista(sorted(productos_insumos_balanceado), datos_insumos_balanceado),
            'productos_campo': sorted(productos_campo),
            'datos_campo': construir_lista(sorted(productos_campo), datos_campo),
        }

        return JsonResponse(response_data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'KARDEX BODEGA DE INSUMOS'
        context['empresas'] = Empresa.objects.all()
        context['piscinas'] = Piscinas.objects.all().order_by('id')  # Listado de todas las piscinas
        return context


# class KardexBodegaGeneralView(TemplateView):
#     template_name = 'app_consumo/kardex_bodega_general.html'
#
#     @method_decorator(csrf_exempt)
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         print("\n" + "=" * 80)
#         print("[KARDEX DEBUG] POST request recibido")
#         print(f"[KARDEX DEBUG] Method: {request.method}")
#         print(f"[KARDEX DEBUG] POST data: {request.POST}")
#         print(f"[KARDEX DEBUG] Content-Type: {request.content_type}")
#         print("=" * 80 + "\n")
#
#         try:
#             action = request.POST.get('action', '')
#             print(f"[KARDEX DEBUG] Action recibida: '{action}'")
#
#             if action == 'get_kardex_horizontal':
#                 print("[KARDEX DEBUG] Ejecutando _get_kardex_horizontal...")
#                 result = self._get_kardex_horizontal(request)
#                 print(f"[KARDEX DEBUG] Resultado type: {type(result)}")
#                 return result
#             else:
#                 print(f"[KARDEX DEBUG] ERROR: Action no válida: '{action}'")
#                 return JsonResponse({'error': f'Action no válida: {action}'}, safe=False)
#         except Exception as e:
#             print(f"[KARDEX DEBUG] ERROR CRÍTICO en kardex: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             return JsonResponse({'error': str(e)}, safe=False)
#
#     def _guess_categoria(self, producto_obj):
#         """
#         Determina la categoría del producto basándose en su nombre o atributos.
#         Retorna: 'balanceado', 'campo', 'camarones', u 'otros'
#         """
#         try:
#             if hasattr(producto_obj, 'categoria') and producto_obj.categoria:
#                 return str(producto_obj.categoria).lower()
#             if hasattr(producto_obj, 'tipo') and producto_obj.tipo:
#                 return str(producto_obj.tipo).lower()
#         except Exception:
#             pass
#
#         nombre = ''
#         try:
#             nombre = (producto_obj.nombre or '') if hasattr(producto_obj, 'nombre') else ''
#         except Exception:
#             pass
#
#         nombre = nombre.lower()
#
#         if any(k in nombre for k in
#                ['balance', 'balanc', 'balanceado', 'exia', 'prime', 'perform', 'focus', 'starter', 'inicio', 'pellet']):
#             return 'balanceado'
#
#         if any(k in nombre for k in ['campo', 'bio', 'natur', 'eco', 'organico', 'carbono', 'siembra', 'hidro']):
#             return 'campo'
#
#         if any(k in nombre for k in ['camaron', 'camarón', 'shrimp', 'aqua', 'larvae', 'post']):
#             return 'camarones'
#
#         return 'otros'
#
#     def _get_kardex_horizontal(self, request):
#         """
#         Obtiene los datos del kardex agrupados por fecha y producto
#         para mostrar una tabla horizontal donde:
#         - Cada fila es una fecha/día
#         - Cada columna es un producto
#         - El valor es el consumo diario de ese producto
#         """
#         print("[KARDEX DEBUG] Iniciando _get_kardex_horizontal")
#
#         start_date = request.POST.get('start_date', '')
#         end_date = request.POST.get('end_date', '')
#         empresa_filter = request.POST.get('empresa', '')
#         piscina_filter = request.POST.get('piscina', '')
#
#         print(f"[KARDEX DEBUG] Filtros recibidos:")
#         print(f"  - start_date: {start_date}")
#         print(f"  - end_date: {end_date}")
#         print(f"  - empresa: {empresa_filter}")
#         print(f"  - piscina: {piscina_filter}")
#
#         qs = Producto_Stock.objects.filter(activo=True).select_related(
#             'producto_empresa',
#             'producto_empresa__nombre_prod',
#             'producto_empresa__nombre_empresa'
#         ).order_by('fecha_ingreso', 'producto_empresa__nombre_prod__nombre')
#
#         print(f"[KARDEX DEBUG] Query base count: {qs.count()}")
#
#         # Filtro por rango de fechas
#         if start_date and end_date:
#             qs = qs.filter(fecha_ingreso__range=[start_date, end_date])
#             print(f"[KARDEX DEBUG] Después de filtro fecha count: {qs.count()}")
#
#         # Filtro por empresa
#         if empresa_filter:
#             try:
#                 eid = int(empresa_filter)
#                 qs = qs.filter(producto_empresa__nombre_empresa__id=eid)
#                 print(f"[KARDEX DEBUG] Filtrado por empresa ID: {eid}, count: {qs.count()}")
#             except Exception:
#                 qs = qs.filter(producto_empresa__nombre_empresa__siglas__iexact=empresa_filter)
#                 print(f"[KARDEX DEBUG] Filtrado por empresa siglas: {empresa_filter}, count: {qs.count()}")
#
#         # Filtro por piscina
#         if piscina_filter:
#             import re
#             numero_match = re.search(r'(\d+)', piscina_filter)
#
#             if numero_match:
#                 numero = numero_match.group(1)
#                 print(f"[KARDEX DEBUG] Número extraído de '{piscina_filter}': {numero}")
#                 qs_filtered = qs.filter(piscinas__iregex=rf'piscina[\s\-_]*{numero}(\s|$)')
#
#                 if qs_filtered.count() > 0:
#                     qs = qs_filtered
#                 else:
#                     variaciones = [
#                         f'PISCINA {numero}',
#                         f'PISCINA-{numero}',
#                         f'Piscina {numero}',
#                         f'Piscina-{numero}',
#                     ]
#                     q_objects = Q()
#                     for var in variaciones:
#                         q_objects |= Q(piscinas__iexact=var)
#                     qs_variaciones = qs.filter(q_objects)
#                     if qs_variaciones.count() > 0:
#                         qs = qs_variaciones
#
#             print(f"[KARDEX DEBUG] Después de filtro piscina '{piscina_filter}' count FINAL: {qs.count()}")
#
#         from collections import defaultdict
#
#         # Diccionario: {fecha: {producto: consumo}}
#         datos_agrupados = defaultdict(lambda: defaultdict(float))
#         productos_set = set()
#         fechas_set = set()
#
#         for item in qs:
#             try:
#                 fecha = item.fecha_ingreso.strftime('%Y-%m-%d') if item.fecha_ingreso else None
#                 if not fecha:
#                     continue
#
#                 producto_obj = getattr(item.producto_empresa, 'nombre_prod', None)
#                 producto_nombre = ''
#
#                 if producto_obj:
#                     producto_nombre = (getattr(producto_obj, 'nombre', None) or
#                                        getattr(producto_obj, 'descripcion', None) or
#                                        str(producto_obj))
#                 else:
#                     producto_nombre = getattr(item.producto_empresa, 'nombre', None) or 'SIN PRODUCTO'
#
#                 if not producto_nombre:
#                     continue
#
#                 # Obtener el consumo (egreso) del día
#                 consumo = float(item.cantidad_egreso or 0)
#
#                 # Agrupar por fecha y producto
#                 datos_agrupados[fecha][producto_nombre] += consumo
#                 productos_set.add(producto_nombre)
#                 fechas_set.add(fecha)
#
#             except Exception as e:
#                 print(f"[KARDEX DEBUG] Error procesando item: {str(e)}")
#                 continue
#
#         # Convertir a formato lista
#         fechas_ordenadas = sorted(list(fechas_set))
#         productos_ordenados = sorted(list(productos_set))
#
#         # Crear estructura de datos para el frontend
#         datos_por_fecha = []
#         for fecha in fechas_ordenadas:
#             fila = {
#                 'fecha': fecha,
#                 'productos': {}
#             }
#             for producto in productos_ordenados:
#                 fila['productos'][producto] = datos_agrupados[fecha].get(producto, 0)
#             datos_por_fecha.append(fila)
#
#         print(f"[KARDEX DEBUG] Total fechas: {len(fechas_ordenadas)}")
#         print(f"[KARDEX DEBUG] Total productos: {len(productos_ordenados)}")
#
#         response_data = {
#             'status': 'ok',
#             'productos': productos_ordenados,
#             'datos': datos_por_fecha
#         }
#
#         return JsonResponse(response_data, safe=False)
#
#     def get_context_data(self, **kwargs):
#
#         context = super().get_context_data(**kwargs)
#         context['titulo'] = 'KARDEX BODEGA DE INSUMOS'
#         context['empresas'] = Empresa.objects.all()
#         return context








