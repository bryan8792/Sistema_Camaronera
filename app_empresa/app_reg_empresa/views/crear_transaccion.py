from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from decimal import Decimal
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..export_utils import export_to_excel, export_to_pdf
from ..initial_data import cargar_tipos_costo_iniciales
from app_empresa.app_reg_empresa.forms import *
from ..models import CostoUtilidadHectarea, Empresa, TipoCosto, CostoOperativo, Piscinas, Produccion, Ciclo


@login_required
def cargar_datos_iniciales(request):
    """
    Vista para cargar los datos iniciales del sistema
    """
    resultado = {
        'status': 'success',
        'message': ''
    }

    try:
        # Cargar tipos de costo
        num_tipos = cargar_tipos_costo_iniciales()
        resultado['message'] = f'Se han cargado {num_tipos} tipos de costo correctamente.'
    except Exception as e:
        resultado['status'] = 'error'
        resultado['message'] = f'Error al cargar datos iniciales: {str(e)}'

    return JsonResponse(resultado)


class CostoUtilidadHectareaView(TemplateView):
    template_name = 'reportes/costo_utilidad_hectarea.html'

    def get(self, request, *args, **kwargs):
        # Verificar si se solicita exportación
        export_format = request.GET.get('export')
        if export_format:
            return self.export_report(request, export_format)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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

        # Obtener empresas para el filtro
        empresas = Empresa.objects.filter(estado=True).order_by('nombre')

        # Calcular resultados
        data = CostoUtilidadHectarea.calcular_todas_piscinas(
            fecha_inicio, fecha_fin, empresa_id
        )

        context.update({
            'resultados': data['resultados'],
            'totales': data['totales'],
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'empresa_id': empresa_id,
            'empresas': empresas,
            'title': 'Reporte de Costo-Utilidad por Hectárea',
        })

        return context

    def export_report(self, request, export_format):
        """
        Exporta el reporte en el formato solicitado
        """
        # Obtener parámetros de filtro
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        empresa_id = request.GET.get('empresa_id')

        # Convertir a objetos date si son strings
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

        # Calcular resultados
        data = CostoUtilidadHectarea.calcular_todas_piscinas(
            fecha_inicio, fecha_fin, empresa_id
        )

        # Preparar datos para exportación
        headers = [
            'Piscina', 'Hectáreas', 'Costos Totales', 'Ingresos Totales',
            'Utilidad Total', 'Costo/Ha', 'Ingreso/Ha', 'Utilidad/Ha', 'Rentabilidad (%)'
        ]

        rows = []
        for r in data['resultados']:
            rows.append([
                r['piscina'],
                r['hectareas'],
                r['costos_totales'],
                r['ingresos_totales'],
                r['utilidad_total'],
                r['costo_por_hectarea'],
                r['ingreso_por_hectarea'],
                r['utilidad_por_hectarea'],
                r['rentabilidad']
            ])

        # Agregar fila de totales
        rows.append([
            'TOTALES',
            data['totales']['hectareas'],
            data['totales']['costos_totales'],
            data['totales']['ingresos_totales'],
            data['totales']['utilidad_total'],
            data['totales']['costo_por_hectarea'],
            data['totales']['ingreso_por_hectarea'],
            data['totales']['utilidad_por_hectarea'],
            data['totales']['rentabilidad']
        ])

        # Configurar datos para exportación
        export_data = {
            'headers': headers,
            'rows': rows,
            'money_columns': [2, 3, 4, 5, 6, 7],  # Columnas con formato de dinero
            'percent_columns': [8],  # Columnas con formato de porcentaje
            'column_widths': [15, 10, 15, 15, 15, 15, 15, 15, 15],
            'subtitle': f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
        }

        # Nombre del archivo
        filename = f"Costo_Utilidad_Hectarea_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}"

        # Exportar en el formato solicitado
        if export_format == 'excel':
            return export_to_excel(export_data, filename, 'Costo-Utilidad')
        elif export_format == 'pdf':
            return export_to_pdf(export_data, filename, 'Reporte de Costo-Utilidad por Hectárea', True)

        # Si no se reconoce el formato, volver a la vista normal
        return super().get(request)


@method_decorator(csrf_exempt, name='dispatch')
class CostoUtilidadHectareaAPIView(TemplateView):
    """
    Vista para proporcionar datos de costo-utilidad en formato JSON para gráficos
    """

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

                data = CostoUtilidadHectarea.desglose_costos_por_tipo(
                    piscina_id, fecha_inicio, fecha_fin
                )

            elif action == 'get_comparativa_piscinas':
                fecha_inicio = request.POST.get('fecha_inicio')
                fecha_fin = request.POST.get('fecha_fin')
                empresa_id = request.POST.get('empresa_id', None)

                # Convertir a objetos date si son strings
                if isinstance(fecha_inicio, str):
                    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                if isinstance(fecha_fin, str):
                    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

                resultados = CostoUtilidadHectarea.calcular_todas_piscinas(
                    fecha_inicio, fecha_fin, empresa_id
                )['resultados']

                # Formatear datos para gráficos
                labels = [r['piscina'] for r in resultados]
                costos = [r['costo_por_hectarea'] for r in resultados]
                ingresos = [r['ingreso_por_hectarea'] for r in resultados]
                utilidades = [r['utilidad_por_hectarea'] for r in resultados]

                data = {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Costo/Ha',
                            'data': costos,
                            'backgroundColor': 'rgba(255, 99, 132, 0.5)',
                        },
                        {
                            'label': 'Ingreso/Ha',
                            'data': ingresos,
                            'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                        },
                        {
                            'label': 'Utilidad/Ha',
                            'data': utilidades,
                            'backgroundColor': 'rgba(75, 192, 192, 0.5)',
                        }
                    ]
                }

            else:
                data['error'] = 'No se reconoce la acción solicitada'

        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data, safe=False)


# Vistas para TipoCosto
class TipoCostoListView(LoginRequiredMixin, ListView):
    model = TipoCosto
    template_name = 'costos/tipo_costo_list.html'
    context_object_name = 'tipos_costo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tipos de Costos'
        return context


class TipoCostoCreateView(CreateView):
    model = TipoCosto
    form_class = TipoCostoForm
    template_name = 'costos/tipo_costo_form.html'
    success_url = reverse_lazy('app_empresa:tipo_costo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Tipo de Costo'
        context['action'] = 'create'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Tipo de costo creado correctamente.')
        return super().form_valid(form)


class TipoCostoUpdateView(UpdateView):
    model = TipoCosto
    form_class = TipoCostoForm
    template_name = 'costos/tipo_costo_form.html'
    success_url = reverse_lazy('app_empresa:tipo_costo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Tipo de Costo'
        context['action'] = 'update'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Tipo de costo actualizado correctamente.')
        return super().form_valid(form)


class TipoCostoDeleteView(DeleteView):
    model = TipoCosto
    template_name = 'costos/tipo_costo_confirm_delete.html'
    success_url = reverse_lazy('app_empresa:tipo_costo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Tipo de Costo'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Tipo de costo eliminado correctamente.')
        return super().delete(request, *args, **kwargs)


# Vistas para CostoOperativo
class CostoOperativoListView(LoginRequiredMixin, ListView):
    model = CostoOperativo
    template_name = 'costos/costo_operativo_list.html'
    context_object_name = 'costos'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros
        piscina_id = self.request.GET.get('piscina_id')
        tipo_costo_id = self.request.GET.get('tipo_costo_id')
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')

        if piscina_id:
            queryset = queryset.filter(piscina_id=piscina_id)

        if tipo_costo_id:
            queryset = queryset.filter(tipo_costo_id=tipo_costo_id)

        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha__gte=fecha_inicio)

        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha__lte=fecha_fin)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Costos Operativos'
        context['piscinas'] = Piscinas.objects.filter(estado=True).order_by('empresa__nombre', 'numero')
        context['tipos_costo'] = TipoCosto.objects.all().order_by('nombre')

        # Filtros actuales
        context['piscina_id'] = self.request.GET.get('piscina_id', '')
        context['tipo_costo_id'] = self.request.GET.get('tipo_costo_id', '')
        context['fecha_inicio'] = self.request.GET.get('fecha_inicio', '')
        context['fecha_fin'] = self.request.GET.get('fecha_fin', '')

        return context


class CostoOperativoCreateView(LoginRequiredMixin, CreateView):
    model = CostoOperativo
    form_class = CostoOperativoForm
    template_name = 'costos/costo_operativo_form.html'
    success_url = reverse_lazy('app_empresa:costo_operativo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Costo Operativo'
        context['action'] = 'create'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Costo operativo registrado correctamente.')
        return super().form_valid(form)


class CostoOperativoUpdateView(LoginRequiredMixin, UpdateView):
    model = CostoOperativo
    form_class = CostoOperativoForm
    template_name = 'costos/costo_operativo_form.html'
    success_url = reverse_lazy('app_empresa:costo_operativo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Costo Operativo'
        context['action'] = 'update'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Costo operativo actualizado correctamente.')
        return super().form_valid(form)


class CostoOperativoDeleteView(LoginRequiredMixin, DeleteView):
    model = CostoOperativo
    template_name = 'costos/costo_operativo_confirm_delete.html'
    success_url = reverse_lazy('app_empresa:costo_operativo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Costo Operativo'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Costo operativo eliminado correctamente.')
        return super().delete(request, *args, **kwargs)


# Vistas para Produccion
class ProduccionListView(LoginRequiredMixin, ListView):
    model = Produccion
    template_name = 'produccion/produccion_list.html'
    context_object_name = 'producciones'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros
        piscina_id = self.request.GET.get('piscina_id')
        ciclo_id = self.request.GET.get('ciclo_id')
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')

        if piscina_id:
            queryset = queryset.filter(piscina_id=piscina_id)

        if ciclo_id:
            queryset = queryset.filter(ciclo_id=ciclo_id)

        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_cosecha__gte=fecha_inicio)

        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_cosecha__lte=fecha_fin)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Producciones'
        context['piscinas'] = Piscinas.objects.filter(estado=True).order_by('empresa__nombre', 'numero')
        context['ciclos'] = Ciclo.objects.all().order_by('-fecha_inicio')

        # Filtros actuales
        context['piscina_id'] = self.request.GET.get('piscina_id', '')
        context['ciclo_id'] = self.request.GET.get('ciclo_id', '')
        context['fecha_inicio'] = self.request.GET.get('fecha_inicio', '')
        context['fecha_fin'] = self.request.GET.get('fecha_fin', '')

        return context


class ProduccionCreateView(LoginRequiredMixin, CreateView):
    model = Produccion
    form_class = ProduccionForm
    template_name = 'produccion/produccion_form.html'
    success_url = reverse_lazy('app_empresa:produccion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Producción'
        context['action'] = 'create'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Producción registrada correctamente.')
        return super().form_valid(form)


class ProduccionUpdateView(LoginRequiredMixin, UpdateView):
    model = Produccion
    form_class = ProduccionForm
    template_name = 'produccion/produccion_form.html'
    success_url = reverse_lazy('app_empresa:produccion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Producción'
        context['action'] = 'update'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Producción actualizada correctamente.')
        return super().form_valid(form)


class ProduccionDeleteView(LoginRequiredMixin, DeleteView):
    model = Produccion
    template_name = 'produccion/produccion_confirm_delete.html'
    success_url = reverse_lazy('app_empresa:produccion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Producción'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Producción eliminada correctamente.')
        return super().delete(request, *args, **kwargs)


# Vistas para Ciclo
class CicloCreateView(LoginRequiredMixin, CreateView):
    model = Ciclo
    form_class = CicloForm
    template_name = 'ciclos/ciclo_form.html'
    success_url = reverse_lazy('app_empresa:produccion_list')  # Redirigir a la lista de producciones

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Ciclo de Producción'
        context['action'] = 'create'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Ciclo de producción registrado correctamente.')
        return super().form_valid(form)


class CicloUpdateView(LoginRequiredMixin, UpdateView):
    model = Ciclo
    form_class = CicloForm
    template_name = 'ciclos/ciclo_form.html'
    success_url = reverse_lazy('app_empresa:produccion_list')  # Redirigir a la lista de producciones

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Ciclo de Producción'
        context['action'] = 'update'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Ciclo de producción actualizado correctamente.')
        return super().form_valid(form)


class CicloDeleteView(LoginRequiredMixin, DeleteView):
    model = Ciclo
    template_name = 'ciclos/ciclo_confirm_delete.html'
    success_url = reverse_lazy('app_empresa:produccion_list')  # Redirigir a la lista de producciones

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Ciclo de Producción'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Ciclo de producción eliminado correctamente.')
        return super().delete(request, *args, **kwargs)


class CostoUtilidadHectareaView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/costo_utilidad_hectarea.html'

    def get(self, request, *args, **kwargs):
        # Verificar si se solicita exportación
        export_format = request.GET.get('export')
        if export_format:
            return self.export_report(request, export_format)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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

        # Obtener empresas para el filtro
        empresas = Empresa.objects.filter(estado=True).order_by('nombre')

        # Calcular resultados
        data = CostoUtilidadHectarea.calcular_todas_piscinas(
            fecha_inicio, fecha_fin, empresa_id
        )

        context.update({
            'resultados': data['resultados'],
            'totales': data['totales'],
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'empresa_id': empresa_id,
            'empresas': empresas,
            'title': 'Reporte de Costo-Utilidad por Hectárea',
        })

        return context

    def export_report(self, request, export_format):
        """
        Exporta el reporte en el formato solicitado
        """
        # Obtener parámetros de filtro
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        empresa_id = request.GET.get('empresa_id')

        # Convertir a objetos date si son strings
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

        # Calcular resultados
        data = CostoUtilidadHectarea.calcular_todas_piscinas(
            fecha_inicio, fecha_fin, empresa_id
        )

        # Preparar datos para exportación
        headers = [
            'Piscina', 'Hectáreas', 'Costos Totales', 'Ingresos Totales',
            'Utilidad Total', 'Costo/Ha', 'Ingreso/Ha', 'Utilidad/Ha', 'Rentabilidad (%)'
        ]

        rows = []
        for r in data['resultados']:
            rows.append([
                r['piscina'],
                r['hectareas'],
                r['costos_totales'],
                r['ingresos_totales'],
                r['utilidad_total'],
                r['costo_por_hectarea'],
                r['ingreso_por_hectarea'],
                r['utilidad_por_hectarea'],
                r['rentabilidad']
            ])

        # Agregar fila de totales
        rows.append([
            'TOTALES',
            data['totales']['hectareas'],
            data['totales']['costos_totales'],
            data['totales']['ingresos_totales'],
            data['totales']['utilidad_total'],
            data['totales']['costo_por_hectarea'],
            data['totales']['ingreso_por_hectarea'],
            data['totales']['utilidad_por_hectarea'],
            data['totales']['rentabilidad']
        ])

        # Configurar datos para exportación
        export_data = {
            'headers': headers,
            'rows': rows,
            'money_columns': [2, 3, 4, 5, 6, 7],  # Columnas con formato de dinero
            'percent_columns': [8],  # Columnas con formato de porcentaje
            'column_widths': [15, 10, 15, 15, 15, 15, 15, 15, 15],
            'subtitle': f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
        }

        # Nombre del archivo
        filename = f"Costo_Utilidad_Hectarea_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}"

        # Exportar en el formato solicitado
        if export_format == 'excel':
            return export_to_excel(export_data, filename, 'Costo-Utilidad')
        elif export_format == 'pdf':
            return export_to_pdf(export_data, filename, 'Reporte de Costo-Utilidad por Hectárea', True)

        # Si no se reconoce el formato, volver a la vista normal
        return super().get(request)


@method_decorator(csrf_exempt, name='dispatch')
class CostoUtilidadHectareaAPIView(LoginRequiredMixin, TemplateView):
    """
    Vista para proporcionar datos de costo-utilidad en formato JSON para gráficos
    """

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

                data = CostoUtilidadHectarea.desglose_costos_por_tipo(
                    piscina_id, fecha_inicio, fecha_fin
                )

            elif action == 'get_comparativa_piscinas':
                fecha_inicio = request.POST.get('fecha_inicio')
                fecha_fin = request.POST.get('fecha_fin')
                empresa_id = request.POST.get('empresa_id', None)

                # Convertir a objetos date si son strings
                if isinstance(fecha_inicio, str):
                    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                if isinstance(fecha_fin, str):
                    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

                resultados = CostoUtilidadHectarea.calcular_todas_piscinas(
                    fecha_inicio, fecha_fin, empresa_id
                )['resultados']

                # Formatear datos para gráficos
                labels = [r['piscina'] for r in resultados]
                costos = [r['costo_por_hectarea'] for r in resultados]
                ingresos = [r['ingreso_por_hectarea'] for r in resultados]
                utilidades = [r['utilidad_por_hectarea'] for r in resultados]

                data = {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Costo/Ha',
                            'data': costos,
                            'backgroundColor': 'rgba(255, 99, 132, 0.5)',
                        },
                        {
                            'label': 'Ingreso/Ha',
                            'data': ingresos,
                            'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                        },
                        {
                            'label': 'Utilidad/Ha',
                            'data': utilidades,
                            'backgroundColor': 'rgba(75, 192, 192, 0.5)',
                        }
                    ]
                }

            else:
                data['error'] = 'No se reconoce la acción solicitada'

        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data, safe=False)


class TipoCostoListView(LoginRequiredMixin, ListView):
    model = TipoCosto
    template_name = 'costos/tipo_costo_list.html'
    context_object_name = 'tipos_costo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tipos de Costos'
        return context


class CostoOperativoListView(LoginRequiredMixin, ListView):
    model = CostoOperativo
    template_name = 'costos/costo_operativo_list.html'
    context_object_name = 'costos'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros
        piscina_id = self.request.GET.get('piscina_id')
        tipo_costo_id = self.request.GET.get('tipo_costo_id')
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')

        if piscina_id:
            queryset = queryset.filter(piscina_id=piscina_id)

        if tipo_costo_id:
            queryset = queryset.filter(tipo_costo_id=tipo_costo_id)

        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha__gte=fecha_inicio)

        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha__lte=fecha_fin)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Costos Operativos'
        context['piscinas'] = Piscinas.objects.filter(estado=True).order_by('empresa__nombre', 'numero')
        context['tipos_costo'] = TipoCosto.objects.all().order_by('nombre')

        # Filtros actuales
        context['piscina_id'] = self.request.GET.get('piscina_id', '')
        context['tipo_costo_id'] = self.request.GET.get('tipo_costo_id', '')
        context['fecha_inicio'] = self.request.GET.get('fecha_inicio', '')
        context['fecha_fin'] = self.request.GET.get('fecha_fin', '')

        return context


class ProduccionListView(LoginRequiredMixin, ListView):
    model = Produccion
    template_name = 'produccion/produccion_list.html'
    context_object_name = 'producciones'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros
        piscina_id = self.request.GET.get('piscina_id')
        ciclo_id = self.request.GET.get('ciclo_id')
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')

        if piscina_id:
            queryset = queryset.filter(piscina_id=piscina_id)

        if ciclo_id:
            queryset = queryset.filter(ciclo_id=ciclo_id)

        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_cosecha__gte=fecha_inicio)

        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_cosecha__lte=fecha_fin)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Producciones'
        context['piscinas'] = Piscinas.objects.filter(estado=True).order_by('empresa__nombre', 'numero')
        context['ciclos'] = Ciclo.objects.all().order_by('-fecha_inicio')

        # Filtros actuales
        context['piscina_id'] = self.request.GET.get('piscina_id', '')
        context['ciclo_id'] = self.request.GET.get('ciclo_id', '')
        context['fecha_inicio'] = self.request.GET.get('fecha_inicio', '')
        context['fecha_fin'] = self.request.GET.get('fecha_fin', '')

        return context

@login_required
def cargar_datos_iniciales(request):
    """
    Vista para cargar los datos iniciales del sistema
    """
    resultado = {
        'status': 'success',
        'message': ''
    }

    try:
        # Cargar tipos de costo
        num_tipos = cargar_tipos_costo_iniciales()
        resultado['message'] = f'Se han cargado {num_tipos} tipos de costo correctamente.'
    except Exception as e:
        resultado['status'] = 'error'
        resultado['message'] = f'Error al cargar datos iniciales: {str(e)}'

    return JsonResponse(resultado)


# Vista para listar ciclos
class CicloListView(LoginRequiredMixin, ListView):
    model = Ciclo
    template_name = 'ciclos/ciclo_list.html'
    context_object_name = 'ciclos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Ciclos de Producción'
        return context


# Añade estas vistas a tu archivo views/crear_transaccion.py

@method_decorator(csrf_exempt, name='dispatch')
class CiclosPorPiscinaView(LoginRequiredMixin, View):
    def get(self, request):
        piscina_id = request.GET.get('piscina_id')
        ciclos = []

        if piscina_id:
            ciclos_obj = Ciclo.objects.filter(piscina_id=piscina_id, activo=True)
            ciclos = [{'id': c.id, 'nombre': c.nombre} for c in ciclos_obj]

        return JsonResponse(ciclos, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class PiscinaInfoView(View):
    def get(self, request):
        piscina_id = request.GET.get('piscina_id')

        if piscina_id:
            try:
                piscina = Piscinas.objects.get(id=piscina_id)
                return JsonResponse({
                    'area': piscina.area,
                    'hectareas': piscina.hectareas
                })
            except Piscinas.DoesNotExist:
                pass

        return JsonResponse({'error': 'Piscina no encontrada'}, status=404)
