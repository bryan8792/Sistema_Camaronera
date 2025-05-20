from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import traceback
import sys
import json
import logging

# Configurar logging
logger = logging.getLogger(__name__)


class DebugTemplateView(View):
    """
    Vista de depuración para verificar problemas con las plantillas
    """

    def get(self, request, *args, **kwargs):
        template_name = request.GET.get('template', 'base.html')
        context = {
            'title': 'Depuración de Plantilla',
            'debug': True,
            'template_name': template_name,
            'test_data': 'Este es un mensaje de prueba para verificar que la plantilla funciona correctamente.'
        }

        try:
            return render(request, template_name, context)
        except Exception as e:
            error_type, error_value, error_traceback = sys.exc_info()
            tb_lines = traceback.format_exception(error_type, error_value, error_traceback)
            error_details = ''.join(tb_lines)

            return HttpResponse(f"""
            <h1>Error al renderizar la plantilla: {template_name}</h1>
            <h2>{str(e)}</h2>
            <pre>{error_details}</pre>
            <h3>Plantillas disponibles:</h3>
            <p>Intenta con estas plantillas:</p>
            <ul>
                <li><a href="?template=base.html">base.html</a></li>
                <li><a href="?template=reportes/costo_utilidad_hectarea.html">reportes/costo_utilidad_hectarea.html</a></li>
                <li><a href="?template=costos/costo_operativo_list.html">costos/costo_operativo_list.html</a></li>
                <li><a href="?template=produccion/produccion_list.html">produccion/produccion_list.html</a></li>
            </ul>
            """, content_type='text/html')


class DebugBlocksView(View):
    """
    Vista para verificar los bloques definidos en las plantillas
    """

    def get(self, request, *args, **kwargs):
        # Definir bloques comunes en Django
        common_blocks = [
            'title', 'content', 'head', 'header', 'footer', 'scripts',
            'css', 'js', 'extra_css', 'extra_js', 'body', 'main',
            'head_content', 'javascript', 'extra_head', 'extra_body'
        ]

        template_name = request.GET.get('template', 'base.html')

        # Crear un contexto con contenido para cada bloque posible
        context = {
            'title': 'Depuración de Bloques',
            'debug': True,
            'template_name': template_name,
        }

        # Renderizar la plantilla con un contenido de prueba para cada bloque
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Depuración de Bloques</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .block-test { margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; }
                .block-name { font-weight: bold; }
                .test-content { background-color: #f0f0f0; padding: 5px; margin-top: 5px; }
            </style>
        </head>
        <body>
            <h1>Depuración de Bloques para: {template}</h1>
            <p>Esta herramienta te ayuda a identificar qué bloques están definidos en la plantilla base.</p>

            <h2>Prueba de Bloques</h2>
            <p>A continuación se muestran los bloques comunes. Los que aparecen con fondo gris son los que están definidos en la plantilla base.</p>

            <div id="block-tests">
        """

        for block in common_blocks:
            # Crear una plantilla temporal que extienda la plantilla base y reemplace cada bloque
            temp_template = f"{{% extends '{template_name}' %}}\n"
            temp_template += f"{{% block {block} %}}\n"
            temp_template += f"<div class='test-content'>Contenido de prueba para el bloque '{block}'</div>\n"
            temp_template += f"{{% endblock %}}\n"

            try:
                # Intentar renderizar la plantilla temporal
                from django.template import Template, Context
                t = Template(temp_template)
                c = Context(context)
                rendered = t.render(c)

                # Si contiene el contenido de prueba, el bloque existe
                if f"Contenido de prueba para el bloque '{block}'" in rendered:
                    html += f"""
                    <div class="block-test">
                        <div class="block-name">✅ Bloque '{block}' encontrado</div>
                        <div class="test-content">Este bloque está definido en la plantilla base.</div>
                    </div>
                    """
                else:
                    html += f"""
                    <div class="block-test">
                        <div class="block-name">❌ Bloque '{block}' no encontrado</div>
                        <div>Este bloque no está definido en la plantilla base o está siendo sobrescrito.</div>
                    </div>
                    """
            except Exception as e:
                html += f"""
                <div class="block-test">
                    <div class="block-name">❓ Bloque '{block}' error</div>
                    <div>Error al probar este bloque: {str(e)}</div>
                </div>
                """

        html += """
            </div>

            <h2>Plantillas disponibles:</h2>
            <ul>
                <li><a href="?template=base.html">base.html</a></li>
                <li><a href="?template=reportes/costo_utilidad_hectarea.html">reportes/costo_utilidad_hectarea.html</a></li>
                <li><a href="?template=costos/costo_operativo_list.html">costos/costo_operativo_list.html</a></li>
                <li><a href="?template=produccion/produccion_list.html">produccion/produccion_list.html</a></li>
            </ul>
        </body>
        </html>
        """

        html = html.format(template=template_name)
        return HttpResponse(html, content_type='text/html')


class DebugCostoUtilidadHectareaView(TemplateView):
    template_name = 'reportes/costo_utilidad_hectarea.html'

    def get(self, request, *args, **kwargs):
        try:
            # Obtener parámetros de filtro
            hoy = datetime.now().date()
            primer_dia_anio = datetime(hoy.year, 1, 1).date()

            fecha_inicio = self.request.GET.get('fecha_inicio', primer_dia_anio.strftime('%Y-%m-%d'))
            fecha_fin = self.request.GET.get('fecha_fin', hoy.strftime('%Y-%m-%d'))
            empresa_id = self.request.GET.get('empresa_id')

            # Convertir a objetos date si son strings
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

            # Importar modelos necesarios
            from ..models import Empresa, CostoUtilidadHectarea

            # Obtener empresas para el filtro
            empresas = Empresa.objects.filter(estado=True).order_by('nombre')

            # Intentar calcular resultados con manejo de errores detallado
            try:
                data = CostoUtilidadHectarea.calcular_todas_piscinas(
                    fecha_inicio, fecha_fin, empresa_id
                )

                # Verificar si data contiene los resultados esperados
                if not data or 'resultados' not in data or 'totales' not in data:
                    error_msg = "El método calcular_todas_piscinas no devolvió los datos esperados"
                    logger.error(f"ERROR: {error_msg}")
                    logger.error(f"DATA: {data}")

                    # Crear datos de ejemplo para depuración
                    data = {
                        'resultados': [
                            {
                                'id': 1,
                                'piscina': 'Piscina de Prueba',
                                'hectareas': 10.0,
                                'costos_totales': 5000.0,
                                'ingresos_totales': 8000.0,
                                'utilidad_total': 3000.0,
                                'costo_por_hectarea': 500.0,
                                'ingreso_por_hectarea': 800.0,
                                'utilidad_por_hectarea': 300.0,
                                'rentabilidad': 60.0
                            }
                        ],
                        'totales': {
                            'hectareas': 10.0,
                            'costos_totales': 5000.0,
                            'ingresos_totales': 8000.0,
                            'utilidad_total': 3000.0,
                            'costo_por_hectarea': 500.0,
                            'ingreso_por_hectarea': 800.0,
                            'utilidad_por_hectarea': 300.0,
                            'rentabilidad': 60.0
                        }
                    }
            except Exception as e:
                logger.error(f"ERROR en calcular_todas_piscinas: {str(e)}")
                traceback.print_exc()

                # Crear datos de ejemplo para depuración
                data = {
                    'resultados': [
                        {
                            'id': 1,
                            'piscina': 'Error en cálculo',
                            'hectareas': 0.0,
                            'costos_totales': 0.0,
                            'ingresos_totales': 0.0,
                            'utilidad_total': 0.0,
                            'costo_por_hectarea': 0.0,
                            'ingreso_por_hectarea': 0.0,
                            'utilidad_por_hectarea': 0.0,
                            'rentabilidad': 0.0
                        }
                    ],
                    'totales': {
                        'hectareas': 0.0,
                        'costos_totales': 0.0,
                        'ingresos_totales': 0.0,
                        'utilidad_total': 0.0,
                        'costo_por_hectarea': 0.0,
                        'ingreso_por_hectarea': 0.0,
                        'utilidad_por_hectarea': 0.0,
                        'rentabilidad': 0.0
                    }
                }

            context = {
                'resultados': data['resultados'],
                'totales': data['totales'],
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'empresa_id': empresa_id,
                'empresas': empresas,
                'title': 'Reporte de Costo-Utilidad por Hectárea (DEBUG)',
                'debug': True
            }

            return render(request, self.template_name, context)

        except Exception as e:
            error_type, error_value, error_traceback = sys.exc_info()
            tb_lines = traceback.format_exception(error_type, error_value, error_traceback)
            error_details = ''.join(tb_lines)

            context = {
                'error': str(e),
                'error_details': error_details,
                'title': 'Error en Reporte de Costo-Utilidad por Hectárea',
                'debug': True
            }

            return render(request, 'reportes/error_debug.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class DebugCostoUtilidadHectareaAPIView(TemplateView):
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', None)
        data = {}

        try:
            if action == 'get_desglose_costos':
                piscina_id = request.POST.get('piscina_id')
                fecha_inicio = request.POST.get('fecha_inicio')
                fecha_fin = request.POST.get('fecha_fin')

                # Convertir a objetos date si son strings
                if isinstance(fecha_inicio, str):
                    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                if isinstance(fecha_fin, str):
                    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

                # Importar modelo necesario
                from ..models import CostoUtilidadHectarea

                try:
                    data = CostoUtilidadHectarea.desglose_costos_por_tipo(
                        piscina_id, fecha_inicio, fecha_fin
                    )
                except Exception as e:
                    logger.error(f"ERROR en desglose_costos_por_tipo: {str(e)}")
                    traceback.print_exc()
                    data = [
                        {'tipo_costo': 'Alimento', 'total': 1000.0},
                        {'tipo_costo': 'Mano de obra', 'total': 800.0},
                        {'tipo_costo': 'Insumos', 'total': 500.0}
                    ]

            else:
                data['error'] = 'No se reconoce la acción solicitada'

        except Exception as e:
            data['error'] = str(e)
            data['traceback'] = traceback.format_exc()

        return JsonResponse(data, safe=False)


class DebugCostoOperativoListView(View):
    """
    Vista de depuración para la lista de costos operativos
    """

    def get(self, request, *args, **kwargs):
        try:
            from ..models import CostoOperativo, Piscinas, TipoCosto

            # Crear datos de ejemplo para depuración
            costos = CostoOperativo.objects.all()[:10]  # Obtener los primeros 10 registros

            # Si no hay datos, crear datos de ejemplo
            if not costos:
                costos = [
                    {
                        'id': 1,
                        'piscina': {'empresa': {'nombre': 'Empresa Ejemplo'}, 'numero': '001'},
                        'tipo_costo': {'nombre': 'Alimento'},
                        'fecha': datetime.now().date(),
                        'monto': 1000.0,
                        'descripcion': 'Costo de ejemplo para depuración'
                    }
                ]

            piscinas = Piscinas.objects.filter(estado=True).order_by('empresa__nombre', 'numero')
            tipos_costo = TipoCosto.objects.all().order_by('nombre')

            context = {
                'title': 'Costos Operativos (DEBUG)',
                'costos': costos,
                'piscinas': piscinas,
                'tipos_costo': tipos_costo,
                'debug': True
            }

            return render(request, 'costos/costo_operativo_list.html', context)

        except Exception as e:
            error_type, error_value, error_traceback = sys.exc_info()
            tb_lines = traceback.format_exception(error_type, error_value, error_traceback)
            error_details = ''.join(tb_lines)

            return HttpResponse(f"""
            <h1>Error en la vista de Costos Operativos</h1>
            <h2>{str(e)}</h2>
            <pre>{error_details}</pre>
            """, content_type='text/html')


class DebugProduccionListView(View):
    """
    Vista de depuración para la lista de producciones
    """

    def get(self, request, *args, **kwargs):
        try:
            from ..models import Produccion, Piscinas, Ciclo

            # Crear datos de ejemplo para depuración
            producciones = Produccion.objects.all()[:10]  # Obtener los primeros 10 registros

            # Si no hay datos, crear datos de ejemplo
            if not producciones:
                producciones = [
                    {
                        'id': 1,
                        'piscina': {'empresa': {'nombre': 'Empresa Ejemplo'}, 'numero': '001'},
                        'ciclo': {'nombre': 'Ciclo 2023-01'},
                        'fecha_cosecha': datetime.now().date(),
                        'cantidad_kg': 1000.0,
                        'precio_venta_kg': 5.0,
                        'total': 5000.0
                    }
                ]

            piscinas = Piscinas.objects.filter(estado=True).order_by('empresa__nombre', 'numero')
            ciclos = Ciclo.objects.all().order_by('-fecha_inicio')

            context = {
                'title': 'Producciones (DEBUG)',
                'producciones': producciones,
                'piscinas': piscinas,
                'ciclos': ciclos,
                'debug': True
            }

            return render(request, 'produccion/produccion_list.html', context)

        except Exception as e:
            error_type, error_value, error_traceback = sys.exc_info()
            tb_lines = traceback.format_exception(error_type, error_value, error_traceback)
            error_details = ''.join(tb_lines)

            return HttpResponse(f"""
            <h1>Error en la vista de Producciones</h1>
            <h2>{str(e)}</h2>
            <pre>{error_details}</pre>
            """, content_type='text/html')
