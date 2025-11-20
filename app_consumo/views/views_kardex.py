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
from app_empresa.app_reg_empresa.models import Empresa
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
        print("\n" + "=" * 80)
        print("[KARDEX DEBUG] POST request recibido")
        print(f"[KARDEX DEBUG] Method: {request.method}")
        print(f"[KARDEX DEBUG] POST data: {request.POST}")
        print(f"[KARDEX DEBUG] Content-Type: {request.content_type}")
        print("=" * 80 + "\n")

        try:
            action = request.POST.get('action', '')
            print(f"[KARDEX DEBUG] Action recibida: '{action}'")

            if action == 'get_kardex_horizontal':
                print("[KARDEX DEBUG] Ejecutando _get_kardex_horizontal...")
                result = self._get_kardex_horizontal(request)
                print(f"[KARDEX DEBUG] Resultado type: {type(result)}")
                return result
            else:
                print(f"[KARDEX DEBUG] ERROR: Action no válida: '{action}'")
                return JsonResponse({'error': f'Action no válida: {action}'}, safe=False)
        except Exception as e:
            print(f"[KARDEX DEBUG] ERROR CRÍTICO en kardex: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, safe=False)

    def _guess_categoria(self, producto_obj):
        """
        Determina la categoría del producto basándose en su nombre o atributos.
        Retorna: 'balanceado', 'campo', 'camarones', u 'otros'
        """
        try:
            if hasattr(producto_obj, 'categoria') and producto_obj.categoria:
                return str(producto_obj.categoria).lower()
            if hasattr(producto_obj, 'tipo') and producto_obj.tipo:
                return str(producto_obj.tipo).lower()
        except Exception:
            pass

        nombre = ''
        try:
            nombre = (producto_obj.nombre or '') if hasattr(producto_obj, 'nombre') else ''
        except Exception:
            pass

        nombre = nombre.lower()

        if any(k in nombre for k in ['balance', 'balanc', 'balanceado', 'exia', 'prime', 'perform', 'focus', 'starter', 'inicio', 'pellet']):
            return 'balanceado'

        if any(k in nombre for k in ['campo', 'bio', 'natur', 'eco', 'organico', 'carbono', 'siembra', 'hidro']):
            return 'campo'

        if any(k in nombre for k in ['camaron', 'camarón', 'shrimp', 'aqua', 'larvae', 'post']):
            return 'camarones'

        return 'otros'

    def _get_kardex_horizontal(self, request):
        """
        Obtiene los datos del kardex en formato horizontal agrupados por empresa/piscina/fecha/producto
        """
        print("[KARDEX DEBUG] Iniciando _get_kardex_horizontal")

        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        empresa_filter = request.POST.get('empresa', '')
        piscina_filter = request.POST.get('piscina', '')

        print(f"[KARDEX DEBUG] Filtros recibidos:")
        print(f"  - start_date: {start_date}")
        print(f"  - end_date: {end_date}")
        print(f"  - empresa: {empresa_filter}")
        print(f"  - piscina: {piscina_filter}")

        # Query base
        qs = Producto_Stock.objects.filter(activo=True).select_related(
            'producto_empresa',
            'producto_empresa__nombre_prod',
            'producto_empresa__nombre_empresa'
        ).order_by('producto_empresa__nombre_empresa__siglas', 'piscinas', 'fecha_ingreso')

        print(f"[KARDEX DEBUG] Query base count: {qs.count()}")

        # Filtro por rango de fechas
        if start_date and end_date:
            qs = qs.filter(fecha_ingreso__range=[start_date, end_date])
            print(f"[KARDEX DEBUG] Después de filtro fecha count: {qs.count()}")

        # Filtro por empresa
        if empresa_filter:
            try:
                eid = int(empresa_filter)
                qs = qs.filter(producto_empresa__nombre_empresa__id=eid)
                print(f"[KARDEX DEBUG] Filtrado por empresa ID: {eid}, count: {qs.count()}")
            except Exception:
                qs = qs.filter(producto_empresa__nombre_empresa__siglas__iexact=empresa_filter)
                print(f"[KARDEX DEBUG] Filtrado por empresa siglas: {empresa_filter}, count: {qs.count()}")

        if piscina_filter:
            # Primero, veamos qué piscinas existen en los datos
            piscinas_disponibles = qs.values_list('piscinas', flat=True).distinct()
            print(f"[KARDEX DEBUG] Piscinas disponibles ANTES del filtro: {list(piscinas_disponibles)[:20]}")

            # Extraer el número de la piscina del filtro (ej: "Piscina-1" -> "1")
            import re
            numero_match = re.search(r'(\d+)', piscina_filter)

            if numero_match:
                numero = numero_match.group(1)
                print(f"[KARDEX DEBUG] Número extraído de '{piscina_filter}': {numero}")

                # Crear filtro con regex para coincidencia exacta del número
                # Este patrón busca: PISCINA<espacio o guion><numero><fin o espacio>
                # Coincidirá con "PISCINA 1", "PISCINA-1", "Piscina 1" pero NO con "PISCINA 10" o "PISCINA 18"
                patron_regex = rf'(?i)piscina[\s\-_]*{numero}(?:\s|$)'

                # Django usa regex de PostgreSQL/MySQL dependiendo del backend
                qs_filtered = qs.filter(piscinas__iregex=rf'piscina[\s\-_]*{numero}(\s|$)')

                print(f"[KARDEX DEBUG] Aplicando regex: {patron_regex}")
                print(f"[KARDEX DEBUG] Después de filtro regex count: {qs_filtered.count()}")

                if qs_filtered.count() > 0:
                    qs = qs_filtered
                    print(f"[KARDEX DEBUG] Filtro aplicado exitosamente")
                else:
                    # Fallback: intentar búsqueda exacta con variaciones comunes
                    variaciones = [
                        f'PISCINA {numero}',
                        f'PISCINA-{numero}',
                        f'Piscina {numero}',
                        f'Piscina-{numero}',
                        f'piscina {numero}',
                        f'piscina-{numero}',
                    ]

                    q_objects = Q()
                    for var in variaciones:
                        q_objects |= Q(piscinas__iexact=var)

                    qs_variaciones = qs.filter(q_objects)
                    print(f"[KARDEX DEBUG] Intentando variaciones exactas, count: {qs_variaciones.count()}")

                    if qs_variaciones.count() > 0:
                        qs = qs_variaciones
                    else:
                        print(
                            f"[KARDEX DEBUG] ADVERTENCIA: No se encontraron registros para piscina '{piscina_filter}'")
            else:
                # Si no se extrajo número, buscar por coincidencia exacta
                qs = qs.filter(piscinas__iexact=piscina_filter)
                print(f"[KARDEX DEBUG] Filtrado por coincidencia exacta: {piscina_filter}")

            print(f"[KARDEX DEBUG] Después de filtro piscina '{piscina_filter}' count FINAL: {qs.count()}")

            # Mostrar qué piscinas quedaron después del filtro
            piscinas_finales = qs.values_list('piscinas', flat=True).distinct()
            print(f"[KARDEX DEBUG] Piscinas en resultado FINAL: {list(piscinas_finales)}")

        # Estructura de datos
        datos = {}
        productos_global = set()
        categorias_map = {}
        items_procesados = 0
        items_con_error = 0

        print(f"[KARDEX DEBUG] Procesando {qs.count()} registros...")

        for item in qs:
            try:
                items_procesados += 1

                fecha = item.fecha_ingreso.strftime('%d-%m-%Y') if item.fecha_ingreso else 'Sin fecha'

                empresa_obj = item.producto_empresa.nombre_empresa
                empresa_siglas = empresa_obj.siglas or (empresa_obj.nombre if hasattr(empresa_obj, 'nombre') else 'N/A')

                piscina = (item.piscinas or 'Todas las Piscinas').strip()

                producto_obj = getattr(item.producto_empresa, 'nombre_prod', None)
                producto_nombre = ''

                if producto_obj:
                    producto_nombre = (getattr(producto_obj, 'nombre', None) or
                                       getattr(producto_obj, 'descripcion', None) or
                                       str(producto_obj))
                else:
                    producto_nombre = getattr(item.producto_empresa, 'nombre', None) or 'SIN PRODUCTO'

                if producto_nombre not in categorias_map:
                    if producto_obj:
                        guessed = self._guess_categoria(producto_obj)
                    else:
                        guessed = 'otros'
                    categorias_map[producto_nombre] = guessed

                productos_global.add(producto_nombre)

                datos.setdefault(empresa_siglas, {})
                datos[empresa_siglas].setdefault(piscina, {})
                datos[empresa_siglas][piscina].setdefault(fecha, {})

                if producto_nombre not in datos[empresa_siglas][piscina][fecha]:
                    datos[empresa_siglas][piscina][fecha][producto_nombre] = {
                        'ingreso': 0.0,
                        'egreso': 0.0,
                        'stock': float(getattr(item.producto_empresa, 'stock', 0) or 0),
                        'unidad': (getattr(producto_obj, 'presentacion', None) if producto_obj else '-') or '-',
                        'categoria': categorias_map[producto_nombre]
                    }

                if item.tipo == 'INGRESO':
                    datos[empresa_siglas][piscina][fecha][producto_nombre]['ingreso'] += float(
                        item.cantidad_ingreso or 0)
                else:
                    datos[empresa_siglas][piscina][fecha][producto_nombre]['egreso'] += float(item.cantidad_egreso or 0)

            except Exception as e:
                items_con_error += 1
                print(f"[KARDEX DEBUG] Error procesando item {getattr(item, 'id', 'NA')}: {str(e)}")
                continue

        productos_ordenados = sorted(list(productos_global))

        print(f"[KARDEX DEBUG] Procesamiento completado:")
        print(f"  - Items procesados: {items_procesados}")
        print(f"  - Items con error: {items_con_error}")
        print(f"  - Empresas encontradas: {len(datos)}")
        print(f"  - Productos únicos: {len(productos_ordenados)}")
        print(f"  - Productos: {productos_ordenados}")

        response_data = {
            'status': 'ok',
            'datos': datos,
            'productos': productos_ordenados,
            'categorias': categorias_map
        }

        response_json = json.dumps(response_data)
        print(f"[KARDEX DEBUG] Tamaño de respuesta JSON: {len(response_json)} bytes")
        print(f"[KARDEX DEBUG] Primeros 200 caracteres: {response_json[:200]}")

        return JsonResponse(response_data, safe=False)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['titulo'] = 'KARDEX BODEGA DE INSUMOS'
        context['empresas'] = Empresa.objects.all()
        return context






