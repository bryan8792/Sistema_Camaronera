
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