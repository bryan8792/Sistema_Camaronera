from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from app_anticipo.models import TipoPago, FormaPagoOpcion, Anticipo, FormaPago
from app_empresa.app_reg_empresa.models import Empresa
from app_contabilidad_planCuentas.models import PlanCuenta
from decimal import Decimal
import json


class AnticipoListView(TemplateView):
    """
    Vista principal para listar y gestionar anticipos
    """
    template_name = 'app_anticipo/anticipo_list.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestión de Anticipos'
        context['empresas'] = Empresa.objects.filter(estado=True)
        context['tipos_pago'] = TipoPago.objects.filter(estado=True)
        context['formas_pago'] = FormaPagoOpcion.objects.filter(estado=True)
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')

            if action == 'list':
                data = self.list_anticipos(request)
            elif action == 'get':
                anticipo_id = request.POST.get('id')
                anticipo = Anticipo.objects.get(pk=anticipo_id)
                data = anticipo.toJSON()
            elif action == 'create':
                data = self.create_anticipo(request)
            elif action == 'update':
                data = self.update_anticipo(request)
            elif action == 'delete':
                data = self.delete_anticipo(request)
            elif action == 'get_plan_cuentas':
                data = self.get_plan_cuentas(request)
            else:
                data['error'] = 'Acción no válida'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def list_anticipos(self, request):
        """Lista todos los anticipos con filtros opcionales"""
        anticipos = Anticipo.objects.select_related('centro_costo', 'categoria_contable').all()

        # Filtros opcionales
        empresa_id = request.POST.get('empresa_id')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        if empresa_id:
            anticipos = anticipos.filter(centro_costo_id=empresa_id)
        if fecha_inicio and fecha_fin:
            anticipos = anticipos.filter(fecha__range=[fecha_inicio, fecha_fin])

        return [anticipo.toJSON() for anticipo in anticipos]

    def create_anticipo(self, request):
        """Crea un nuevo anticipo con sus formas de pago"""
        with transaction.atomic():
            # Crear el anticipo
            anticipo = Anticipo()
            anticipo.caja = request.POST.get('caja', 'PRINCIPAL')
            anticipo.tipo_cliente = request.POST.get('tipo_cliente', 'CLIENTE')
            anticipo.centro_costo_id = request.POST.get('centro_costo_id')
            anticipo.tipo_identificacion = request.POST.get('tipo_identificacion', 'CEDULA')
            anticipo.identificacion = request.POST.get('identificacion')
            anticipo.razon_social = request.POST.get('razon_social')
            anticipo.nombre_comercial = request.POST.get('nombre_comercial', '')
            anticipo.telefono = request.POST.get('telefono', '')
            anticipo.celular = request.POST.get('celular', '')
            anticipo.email = request.POST.get('email', '')
            anticipo.ciudad = request.POST.get('ciudad', '')
            anticipo.direccion = request.POST.get('direccion', '')
            anticipo.fecha = request.POST.get('fecha')
            anticipo.monto = Decimal(request.POST.get('monto', 0))
            anticipo.concepto = request.POST.get('concepto', '')

            categoria_contable_id = request.POST.get('categoria_contable_id')
            if categoria_contable_id:
                anticipo.categoria_contable_id = categoria_contable_id

            anticipo.save()

            # Crear las formas de pago
            formas_pago_json = request.POST.get('formas_pago', '[]')
            formas_pago_data = json.loads(formas_pago_json)

            total_formas_pago = Decimal('0.00')
            for fp_data in formas_pago_data:
                forma_pago = FormaPago()
                forma_pago.anticipo = anticipo
                forma_pago.tipo_id = fp_data.get('tipo_id')
                forma_pago.forma_id = fp_data.get('forma_id')
                forma_pago.valor = Decimal(fp_data.get('valor', 0))
                forma_pago.referencia = fp_data.get('referencia', '')
                forma_pago.banco = fp_data.get('banco', '')
                forma_pago.observacion = fp_data.get('observacion', '')
                forma_pago.save()
                total_formas_pago += forma_pago.valor

            # Validar que el total de formas de pago coincida con el monto
            if total_formas_pago != anticipo.monto:
                raise Exception(
                    f'El total de formas de pago ({total_formas_pago}) no coincide con el monto ({anticipo.monto})')

            return {'success': True, 'message': 'Anticipo creado exitosamente', 'anticipo': anticipo.toJSON()}

    def update_anticipo(self, request):
        """Actualiza un anticipo existente"""
        with transaction.atomic():
            anticipo_id = request.POST.get('id')
            anticipo = Anticipo.objects.get(pk=anticipo_id)

            # Actualizar campos
            anticipo.caja = request.POST.get('caja', anticipo.caja)
            anticipo.tipo_cliente = request.POST.get('tipo_cliente', anticipo.tipo_cliente)
            anticipo.centro_costo_id = request.POST.get('centro_costo_id', anticipo.centro_costo_id)
            anticipo.tipo_identificacion = request.POST.get('tipo_identificacion', anticipo.tipo_identificacion)
            anticipo.identificacion = request.POST.get('identificacion', anticipo.identificacion)
            anticipo.razon_social = request.POST.get('razon_social', anticipo.razon_social)
            anticipo.nombre_comercial = request.POST.get('nombre_comercial', anticipo.nombre_comercial)
            anticipo.telefono = request.POST.get('telefono', anticipo.telefono)
            anticipo.celular = request.POST.get('celular', anticipo.celular)
            anticipo.email = request.POST.get('email', anticipo.email)
            anticipo.ciudad = request.POST.get('ciudad', anticipo.ciudad)
            anticipo.direccion = request.POST.get('direccion', anticipo.direccion)
            anticipo.fecha = request.POST.get('fecha', anticipo.fecha)
            anticipo.monto = Decimal(request.POST.get('monto', anticipo.monto))
            anticipo.concepto = request.POST.get('concepto', anticipo.concepto)

            categoria_contable_id = request.POST.get('categoria_contable_id')
            if categoria_contable_id:
                anticipo.categoria_contable_id = categoria_contable_id

            anticipo.save()

            # Eliminar formas de pago existentes y crear nuevas
            anticipo.formas_pago.all().delete()

            formas_pago_json = request.POST.get('formas_pago', '[]')
            formas_pago_data = json.loads(formas_pago_json)

            for fp_data in formas_pago_data:
                forma_pago = FormaPago()
                forma_pago.anticipo = anticipo
                forma_pago.tipo_id = fp_data.get('tipo_id')
                forma_pago.forma_id = fp_data.get('forma_id')
                forma_pago.valor = Decimal(fp_data.get('valor', 0))
                forma_pago.referencia = fp_data.get('referencia', '')
                forma_pago.banco = fp_data.get('banco', '')
                forma_pago.observacion = fp_data.get('observacion', '')
                forma_pago.save()

            return {'success': True, 'message': 'Anticipo actualizado exitosamente', 'anticipo': anticipo.toJSON()}

    def delete_anticipo(self, request):
        """Elimina (desactiva) un anticipo"""
        anticipo_id = request.POST.get('id')
        anticipo = Anticipo.objects.get(pk=anticipo_id)
        anticipo.estado = False
        anticipo.save()
        return {'success': True, 'message': 'Anticipo eliminado exitosamente'}

    def get_plan_cuentas(self, request):
        """Obtiene el plan de cuentas filtrado por empresa"""
        empresa_id = request.POST.get('empresa_id')

        # Filtrar cuentas contables relacionadas con anticipos de clientes
        cuentas = PlanCuenta.objects.filter(estado=True)

        # Si tienes un campo empresa en PlanCuenta, filtra por empresa
        # cuentas = cuentas.filter(empresa_id=empresa_id)

        # Filtrar por cuentas de anticipos (ajusta según tu plan de cuentas)
        cuentas = cuentas.filter(codigo__icontains='2.1.1.04')  # Ejemplo: Anticipos de clientes

        return [{'id': c.id, 'codigo': c.codigo, 'nombre': c.nombre, 'descripcion': f"{c.codigo} - {c.nombre}"} for c in
                cuentas]


class TipoPagoListView(TemplateView):
    """
    Vista para gestionar tipos de pago (CONTADO, CREDITO, etc.)
    """
    template_name = 'app_anticipo/tipo_pago_list.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Tipos de Pago'
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')

            if action == 'list':
                tipos = TipoPago.objects.all()
                data = [tipo.toJSON() for tipo in tipos]
            elif action == 'create':
                tipo = TipoPago()
                tipo.nombre = request.POST.get('nombre')
                tipo.descripcion = request.POST.get('descripcion', '')
                tipo.save()
                data = {'success': True, 'message': 'Tipo de pago creado exitosamente', 'tipo': tipo.toJSON()}
            elif action == 'update':
                tipo_id = request.POST.get('id')
                tipo = TipoPago.objects.get(pk=tipo_id)
                tipo.nombre = request.POST.get('nombre', tipo.nombre)
                tipo.descripcion = request.POST.get('descripcion', tipo.descripcion)
                tipo.save()
                data = {'success': True, 'message': 'Tipo de pago actualizado exitosamente', 'tipo': tipo.toJSON()}
            elif action == 'delete':
                tipo_id = request.POST.get('id')
                tipo = TipoPago.objects.get(pk=tipo_id)
                tipo.estado = False
                tipo.save()
                data = {'success': True, 'message': 'Tipo de pago eliminado exitosamente'}
            else:
                data['error'] = 'Acción no válida'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


class FormaPagoOpcionListView(TemplateView):
    """
    Vista para gestionar formas de pago (EFECTIVO, CHEQUE, TRANSFERENCIA, etc.)
    """
    template_name = 'app_anticipo/forma_pago_list.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Formas de Pago'
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')

            if action == 'list':
                formas = FormaPagoOpcion.objects.all()
                data = [forma.toJSON() for forma in formas]
            elif action == 'create':
                forma = FormaPagoOpcion()
                forma.nombre = request.POST.get('nombre')
                forma.descripcion = request.POST.get('descripcion', '')
                forma.codigo = request.POST.get('codigo', '')
                forma.save()
                data = {'success': True, 'message': 'Forma de pago creada exitosamente', 'forma': forma.toJSON()}
            elif action == 'update':
                forma_id = request.POST.get('id')
                forma = FormaPagoOpcion.objects.get(pk=forma_id)
                forma.nombre = request.POST.get('nombre', forma.nombre)
                forma.descripcion = request.POST.get('descripcion', forma.descripcion)
                forma.codigo = request.POST.get('codigo', forma.codigo)
                forma.save()
                data = {'success': True, 'message': 'Forma de pago actualizada exitosamente', 'forma': forma.toJSON()}
            elif action == 'delete':
                forma_id = request.POST.get('id')
                forma = FormaPagoOpcion.objects.get(pk=forma_id)
                forma.estado = False
                forma.save()
                data = {'success': True, 'message': 'Forma de pago eliminada exitosamente'}
            else:
                data['error'] = 'Acción no válida'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


class AnticipoFormView(TemplateView):
    """
    Vista del formulario de anticipo (página completa, no modal)
    """
    template_name = 'app_anticipo/anticipo_form.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Formulario de Anticipo'
        context['empresas'] = Empresa.objects.filter(estado=True)
        context['tipos_pago'] = TipoPago.objects.filter(estado=True)
        context['formas_pago'] = FormaPagoOpcion.objects.filter(estado=True)
        return context
