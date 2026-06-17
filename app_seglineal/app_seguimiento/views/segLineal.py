import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import *
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from app_empresa.app_reg_empresa.models import Piscinas, Empresa
from app_seglineal.app_seguimiento.models import TransferenciaLarva, DetalleTransferenciaLarva
from app_stock.app_detalle_stock.models import Producto_Stock


# METODO PARA LISTAR LA VENTANA PRINCIPAL DEL SEGUIMIENTO
class listarSeguimientoView(ListView):
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
        context['nombre'] = 'Seguimiento Lineal'
        context['seguimiento'] = Piscinas.objects.all()
        context['piscinas'] = Piscinas.objects.all()
        return context


# VENTANA PAR LISTAR EL SEGUIMIENTO POR DETALLES DE BUSQUEDA EJEMPLO: ID
class listarSeguimientoPiscinasView(ListView):
    model = Piscinas
    template_name = 'app_consumo_piscinas/consumo_piscina_detalle.html'

    # def get_queryset(self):
    #     return Piscinas.objects.filter(numero__icontains=(self.kwargs['pk']), empresa__piscinas__numero__icontains=Piscinas.objects.get(id=self.kwargs['pk']).numero)

    # def get_queryset(self):
    #   return Producto_Stock.objects.filter(producto_empresa__nombre_empresa__siglas__icontains=Piscinas.objects.get(id=self.kwargs['pk']).empresa.siglas, activo__exact=True)

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Piscinas.objects.get(id=self.kwargs['pk']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Kardex Stock Productos PSM'
        context['numero'] = Piscinas.objects.filter(id=self.kwargs['pk'])
        context['numero_piscina'] = Piscinas.objects.get(id=self.kwargs['pk']).numero
        context['detalle'] = Producto_Stock.objects.filter(piscinas__exact=Piscinas.objects.get(id=self.kwargs['pk']).numero, activo__exact=True)
        return context


# LISTAR TRANSFERENCIA
class listarTransferenciaLarvaView(ListView):

    model = TransferenciaLarva
    template_name = 'app_seglineal/listar_transferencia_larva.html'

    def get_queryset(self):
        return TransferenciaLarva.objects.select_related('usuario').order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Transferencia de Larvas'
        return context


class CrearTransferenciaLarvaView(TemplateView):
    template_name = 'app_seglineal/crear_transferencia.html'
    success_url = reverse_lazy('app_seglineal:listado')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_piscinas':
                data = []
                empresa = request.POST['empresa']
                for p in Piscinas.objects.filter(
                        empresa__siglas=empresa,
                        estado=True):
                    data.append({
                        'id': p.id,
                        'nombre': p.numero
                    })


            elif action == 'create':

                with transaction.atomic():

                    cabecera = TransferenciaLarva.objects.create(

                        fecha_larva_sembrada=request.POST.get(

                            'fecha_larva_sembrada'

                        ),

                        cantidad_larva_sembrada=request.POST.get(

                            'cantidad_larva_sembrada'

                        ),

                        fecha_siembra_piscina=request.POST.get(

                            'fecha_siembra_piscina'

                        ),

                        laboratorio=request.POST.get(

                            'laboratorio'

                        ),

                        usuario=request.user

                    )

                    items = json.loads(

                        request.POST.get('items', '[]')

                    )

                    for i in items:
                        piscina = Piscinas.objects.get(

                            id=i['hacia_p']

                        )

                        DetalleTransferenciaLarva.objects.create(

                            transferencia=cabecera,

                            desde_piscina=i['desde_p'],

                            maduracion=i['maduracion'],

                            hacia_piscina=piscina,

                            sector=i['sector'],

                            hectareas=Decimal(

                                i['ha'] or 0

                            ),

                            animales_sembrados=Decimal(

                                i['animales'] or 0

                            ),

                            peso_siembra=Decimal(

                                i['peso'] or 0

                            ),

                            animales_ha=Decimal(

                                i['animha'] or 0

                            ),

                            edad=int(

                                i['edad'] or 0

                            ),

                            total_transferido=Decimal(

                                i['transferido'] or 0

                            ),

                            porcentaje_sobrevivencia=Decimal(

                                i['sobrev'] or 0

                            ),

                            aguaje=i['aguaje'],

                            numero_guia=i['guia'],

                            observacion=i['observacion']

                        )

                    data['success'] = True

            else:
                data['error'] = 'Acción inválida'

        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresas'] = Empresa.objects.filter(estado=True)
        return context


class detalleTransferenciaLarvaView(DetailView):
    model = TransferenciaLarva
    template_name = 'app_seglineal/detalle_transferencia_larva.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Detalle Transferencia Larva'
        return context


class editarTransferenciaLarvaView(UpdateView):
    model = TransferenciaLarva
    fields = [
        'fecha_larva_sembrada',
        'cantidad_larva_sembrada',
        'fecha_siembra_piscina',
        'laboratorio'
    ]
    template_name = 'app_seglineal/editar_transferencia_larva.html'
    success_url = reverse_lazy('app_seguimiento_lineal:listar_transferencia')


class eliminarTransferenciaLarvaView(DeleteView):
    model = TransferenciaLarva
    template_name = 'app_seglineal/eliminar_transferencia_larva.html'
    success_url = reverse_lazy('app_seguimiento_lineal:listar_transferencia')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Transferencia de Larvas'
        return context


# app_seglineal/app_seguimiento/views/segLineal.py
class DashboardTransferenciaLarvaView(TemplateView):
    template_name = 'app_seglineal/dashboard_transferencia.html'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'grafico':
                laboratorio = request.POST.get('laboratorio')
                sector = request.POST.get('sector')
                desde = request.POST.get('desde')
                detalle = DetalleTransferenciaLarva.objects.select_related('transferencia', 'hacia_piscina')

                if laboratorio:
                    detalle = detalle.filter(transferencia__laboratorio=laboratorio)

                if sector:
                    detalle = detalle.filter(sector=sector)

                if desde:
                    detalle = detalle.filter(desde_piscina=desde)

                categorias = []
                supervivencia = []
                animales = []

                for d in detalle:
                    categorias.append(str(d.hacia_piscina.numero))
                    supervivencia.append(float(d.porcentaje_sobrevivencia))
                    animales.append(float(d.animales_sembrados))
                data = {
                    'categorias': categorias,
                    'supervivencia': supervivencia,
                    'animales': animales
                }

        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['laboratorios'] = (TransferenciaLarva.objects.values_list('laboratorio', flat=True).distinct())
        context['sectores'] = (DetalleTransferenciaLarva.objects.values_list('sector', flat=True).distinct())
        context['desde_piscinas'] = (DetalleTransferenciaLarva.objects.values_list('desde_piscina', flat=True).distinct())
        return context