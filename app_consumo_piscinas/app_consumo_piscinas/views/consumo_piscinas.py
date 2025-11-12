
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from app_consumo_piscinas.app_consumo_piscinas.forms import ReportForm
from app_empresa.app_reg_empresa.models import Piscinas
from app_stock.app_detalle_stock.models import Producto_Stock
from django.db.models.functions import Cast
from django.db.models import IntegerField

# METODO PARA LISTAR LA VENTANA PRINCIPAL DEL CONSUMO DE PISCINAS
class listarConsumoView(ListView):
    model = Piscinas
    template_name = 'app_consumo_piscinas/consumo_piscina_principal.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Producto_Stock.objects.get(pk=request.POST['id']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Consumo por Piscinas'
        context['seguimiento'] = Piscinas.objects.all()
        context['piscinas'] = Piscinas.objects.all()
        return context




# VENTANA PAR LISTAR EL CONSUMO DE PISCINAS POR DETALLES DE BUSQUEDA EJEMPLO: ID
class listarConsumoPiscinasView(ListView):
    model = Piscinas
    template_name = 'app_consumo_piscinas/consumo_piscina_detalle.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_detalle_consumo':
                data = []
                searchdata = Producto_Stock.objects.filter(piscinas__exact=Piscinas.objects.get(id=self.kwargs['pk']).numero, activo__exact=True)
                for i in searchdata:
                    data.append(i.toJSON())
            elif action == 'search_report_insumos':
                print('Se busco por Insumos por Piscinas')
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                searchdata = Producto_Stock.objects.filter(piscinas__exact=Piscinas.objects.get(id=self.kwargs['pk']).numero, activo__exact=True)
                if len(start_date) and len(end_date):
                    searchdata = searchdata.filter(fecha_ingreso__range=[start_date, end_date])
                for i in searchdata:
                    data.append(i.toJSON())
            elif action == 'search_piscinas_insumos':
                print('Se busco por Piscinas por los Insumos')
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                searchdata = Producto_Stock.objects.filter(piscinas__exact=Piscinas.objects.get(id=self.kwargs['pk']).numero, activo__exact=True)
                if len(start_date) and len(end_date):
                    searchdata = searchdata.filter(fecha_ingreso__range=[start_date, end_date])
                for i in searchdata:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'CONSUMO POR PISCINAS'
        context['numero'] = Piscinas.objects.filter(id=self.kwargs['pk'])
        context['numero_piscina'] = Piscinas.objects.get(id=self.kwargs['pk']).numero
        #context['detalle'] = Producto_Stock.objects.filter(piscinas__exact=Piscinas.objects.get(id=self.kwargs['pk']).numero, activo__exact=True)
        context['form'] = ReportForm()
        return context




# VENTANA PAR LISTAR EL CONSUMO DE PISCINAS POR DETALLES DE BUSQUEDA EJEMPLO: ID
class listarConsumoGeneralView(ListView):
    model = Piscinas
    template_name = 'app_consumo_piscinas/consumo_piscina_conglomerado_general.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_report_insumos_conglomerado':
                print('Se busco por Conglomerado General de Consumos')
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                searchdata = Producto_Stock.objects.filter(activo__exact=True).exclude(piscinas__exact='Todas las Piscinas')
                if len(start_date) and len(end_date):
                    searchdata = searchdata.filter(fecha_ingreso__range=[start_date, end_date])
                for i in searchdata:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = ''+e
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'CONSUMO POR PISCINAS'
        context['numero'] = Piscinas.objects.all()
        context['numero_piscina'] = Piscinas.objects.all()
        #context['detalle'] = Producto_Stock.objects.filter(piscinas__exact=Piscinas.objects.get(id=self.kwargs['pk']).numero, activo__exact=True)
        context['form'] = ReportForm()
        return context


class listarConsumoGeneralEmpresasView(ListView):
    model = Piscinas
    template_name = 'app_consumo_piscinas/consumo_piscina_conglomerado_general_empresas.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_report_insumos_conglomerado':
                print('=== BUSCANDO CONGLOMERADO GENERAL ===')
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                empresa = request.POST.get('empresa', '')

                print(f'[BACKEND] Parámetros recibidos:')
                print(f'[BACKEND] - Empresa: "{empresa}"')
                print(f'[BACKEND] - Fecha inicio: "{start_date}"')
                print(f'[BACKEND] - Fecha fin: "{end_date}"')

                # QUERY BASE - EXCLUIR "TODAS LAS PISCINAS"
                searchdata = Producto_Stock.objects.filter(
                    activo=True
                ).exclude(
                    piscinas='Todas las Piscinas'
                )

                print(f'[BACKEND] Registros antes de filtrar: {searchdata.count()}')

                # FILTRO POR EMPRESA - CORREGIDO
                if empresa and empresa != "":
                    print(f'[BACKEND] Aplicando filtro para empresa: {empresa}')

                    # Obtener TODAS las piscinas de esta empresa
                    piscinas_empresa = Piscinas.objects.filter(
                        empresa__siglas=empresa
                    )

                    # Extraer los números de piscina
                    numeros_piscinas = list(piscinas_empresa.values_list('numero', flat=True))
                    print(f'[BACKEND] Piscinas de {empresa}: {numeros_piscinas}')

                    if numeros_piscinas:
                        # Filtrar por los números de piscina
                        searchdata = searchdata.filter(piscinas__in=numeros_piscinas)
                    else:
                        # Si no hay piscinas, mostrar vacío
                        searchdata = searchdata.none()

                    print(f'[BACKEND] Registros después de filtrar por empresa: {searchdata.count()}')

                # FILTRO POR FECHAS
                if start_date and end_date:
                    searchdata = searchdata.filter(fecha_ingreso__range=[start_date, end_date])
                    print(f'[BACKEND] Registros después de filtrar por fecha: {searchdata.count()}')

                # DEBUG: Mostrar primeros registros
                print(f'[BACKEND] === REGISTROS ENCONTRADOS ===')
                for i, item in enumerate(searchdata[:3]):
                    print(f'[BACKEND] Registro {i}: Piscina="{item.piscinas}"')

                # CONVERTIR A JSON
                for i in searchdata:
                    item_data = i.toJSON()
                    # Agregar información de empresa para debugging
                    try:
                        piscina_obj = Piscinas.objects.get(numero=i.piscinas)
                        item_data['empresa_info'] = piscina_obj.empresa.siglas
                    except:
                        item_data['empresa_info'] = 'No encontrada'
                    data.append(item_data)

                print(f'[BACKEND] Total registros retornados: {len(data)}')

            else:
                data = {'error': 'Acción no válida'}
        except Exception as e:
            print(f'[BACKEND] ERROR: {str(e)}')
            import traceback
            print(f'[BACKEND] TRACEBACK: {traceback.format_exc()}')
            data = {'error': str(e)}
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'CONSUMO POR PISCINAS'
        context['numero'] = Piscinas.objects.all()
        context['numero_piscina'] = Piscinas.objects.all()
        context['form'] = ReportForm()
        return context


# VENTANA PAR LISTAR EL CONSUMO DE PISCINAS POR DETALLES DE BUSQUEDA EJEMPLO: ID
class listarResumenGeneralView(ListView):
    model = Piscinas
    template_name = 'app_consumo_piscinas/resumen_consumo_conglomerado_general.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_piscinas_insumos_conglomerado':
                print('Se busco por Piscinas por los Insumos')
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                searchdata = Producto_Stock.objects.filter(activo__exact=True).exclude(piscinas__exact='Todas las Piscinas')
                if len(start_date) and len(end_date):
                    searchdata = searchdata.filter(fecha_ingreso__range=[start_date, end_date])
                for i in searchdata:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = ''+e
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'RESUMEN CONSUMO POR PRODUCTO'
        context['detail'] = 'RESUMEN CONGLOMERADO GENERAL DE CONSUMO'
        context['numero'] = Piscinas.objects.all()
        context['numero_piscina'] = Piscinas.objects.all()
        context['form'] = ReportForm()
        return context



# VENTANA PAR LISTAR EL CONSUMO DE PISCINAS POR DETALLES POR EMPRESA PSM DE BUSQUEDA EJEMPLO: ID
class listarResumenGeneralPSMView(ListView):
    model = Piscinas
    template_name = 'app_consumo_piscinas/resumen_consumo_conglomerado_psm.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_insumos_conglomerado_psm':
                print('Se busco por Piscinas por los Insumos')
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                searchdata = Producto_Stock.objects.filter(activo__exact=True, producto_empresa__nombre_empresa__siglas__icontains='PSM').exclude(piscinas__exact='Todas las Piscinas')
                if len(start_date) and len(end_date):
                    searchdata = searchdata.filter(fecha_ingreso__range=[start_date, end_date])
                for i in searchdata:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = ''+e
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'RESUMEN CONSUMO POR PRODUCTOS'
        context['detail'] = 'RESUMEN CONSUMO EMPRESA PSM'
        context['numero'] = Piscinas.objects.all()
        context['numero_piscina'] = Piscinas.objects.all()
        #context['detalle'] = Producto_Stock.objects.filter(piscinas__exact=Piscinas.objects.get(id=self.kwargs['pk']).numero, activo__exact=True)
        context['form'] = ReportForm()
        return context


# VENTANA PAR LISTAR EL CONSUMO DE PISCINAS POR DETALLES POR EMPRESA PSM DE BUSQUEDA EJEMPLO: ID
class listarResumenGeneralPSMLineaView(ListView):
    model = Piscinas
    template_name = 'app_consumo_piscinas/consumo_por_linea/resumen_consumo_psm_linea.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_insumos_conglomerado_psm_linea':
                print('Se busco por Piscinas por los Insumos')
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                searchdata = Producto_Stock.objects.filter(activo__exact=True, producto_empresa__nombre_empresa__siglas__icontains='PSM').exclude(piscinas__exact='Todas las Piscinas')
                if len(start_date) and len(end_date):
                    searchdata = searchdata.filter(fecha_ingreso__range=[start_date, end_date])
                for i in searchdata:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = ''+e
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'RESUMEN CONSUMO POR PRODUCTOS'
        context['detail'] = 'RESUMEN CONSUMO EMPRESA PSM'
        context['numero'] = Piscinas.objects.all()
        context['numero_piscina'] = Piscinas.objects.all()
        #context['detalle'] = Producto_Stock.objects.filter(piscinas__exact=Piscinas.objects.get(id=self.kwargs['pk']).numero, activo__exact=True)
        context['form'] = ReportForm()
        return context



# VENTANA PAR LISTAR EL CONSUMO DE PISCINAS POR DETALLES POR EMPRESA PSM DE BUSQUEDA EJEMPLO: ID
class listarResumenGeneralBIOView(ListView):
    model = Piscinas
    template_name = 'app_consumo_piscinas/resumen_consumo_conglomerado_bio.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_insumos_conglomerado_bio':
                print('Se busco por Piscinas por los Insumos')
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                searchdata = Producto_Stock.objects.filter(activo__exact=True, producto_empresa__nombre_empresa__siglas__icontains='BIO').exclude(piscinas__exact='Todas las Piscinas')
                if len(start_date) and len(end_date):
                    searchdata = searchdata.filter(fecha_ingreso__range=[start_date, end_date])
                for i in searchdata:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = ''+e
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'RESUMEN CONSUMO POR PRODUCTOS'
        context['detail'] = 'RESUMEN CONSUMO EMPRESA BIO'
        context['numero'] = Piscinas.objects.all()
        context['numero_piscina'] = Piscinas.objects.all()
        #context['detalle'] = Producto_Stock.objects.filter(piscinas__exact=Piscinas.objects.get(id=self.kwargs['pk']).numero, activo__exact=True)
        context['form'] = ReportForm()
        return context