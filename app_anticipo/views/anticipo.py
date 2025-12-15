# app_anticipo/views/anticipo.py

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db import transaction
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from app_anticipo.models import Anticipo, FormaPago, TipoPago, FormaPagoOpcion
from app_empresa.app_reg_empresa.models import Empresa
from app_contabilidad_planCuentas.models import PlanCuenta
from datetime import datetime
from decimal import Decimal
import json


class AnticipoFormView(TemplateView):
    template_name = 'app_anticipos/anticipo_form.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Formulario de Anticipo'
        context['empresas'] = Empresa.objects.filter(estado=True)
        context['tipos_pago'] = TipoPago.objects.filter(estado=True)
        context['formas_pago'] = FormaPagoOpcion.objects.filter(estado=True)

        # Si hay un ID en la URL, cargar el anticipo para editar
        anticipo_id = self.kwargs.get('pk') or self.request.GET.get('id')
        if anticipo_id:
            try:
                anticipo = Anticipo.objects.select_related('centro_costo', 'categoria_contable').get(pk=anticipo_id)
                context['anticipo'] = anticipo
                context['titulo'] = f'Editar Anticipo #{anticipo_id}'
            except Anticipo.DoesNotExist:
                pass

        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            print(f"[DEBUG] Acción recibida: {action}")

            if action == 'create':
                data = self.create_anticipo(request)
            elif action == 'update':
                data = self.update_anticipo(request)
            elif action == 'get':
                data = self.get_anticipo(request)
            elif action == 'get_plan_cuentas':
                data = self.get_plan_cuentas(request)
            else:
                data['error'] = 'Acción no válida'
        except Exception as e:
            data['error'] = str(e)
            import traceback
            traceback.print_exc()
        return JsonResponse(data, safe=False)

    def get_anticipo(self, request):
        """Obtiene un anticipo por ID con sus formas de pago"""
        anticipo_id = request.POST.get('id')
        print(f"[DEBUG] get_anticipo - ID recibido: {anticipo_id}")

        if not anticipo_id:
            return {'error': 'ID de anticipo no proporcionado'}

        try:
            anticipo = Anticipo.objects.select_related('centro_costo', 'categoria_contable').get(pk=anticipo_id)

            # Crear estructura de datos manualmente para evitar problemas de unicode
            anticipo_data = {
                'id': anticipo.id,
                'caja': anticipo.caja,
                'tipo_cliente': anticipo.tipo_cliente,
                'centro_costo_id': anticipo.centro_costo.id if anticipo.centro_costo else None,
                'centro_costo_nombre': anticipo.centro_costo.siglas if anticipo.centro_costo else '',
                'tipo_identificacion': anticipo.tipo_identificacion,
                'identificacion': anticipo.identificacion or '',
                'razon_social': anticipo.razon_social or '',
                'nombre_comercial': anticipo.nombre_comercial or '',
                'telefono': anticipo.telefono or '',
                'celular': anticipo.celular or '',
                'email': anticipo.email or '',
                'ciudad': anticipo.ciudad or '',
                'direccion': anticipo.direccion or '',
                'fecha': str(anticipo.fecha) if anticipo.fecha else '',
                'monto': float(anticipo.monto),
                'concepto': anticipo.concepto or '',
                'categoria_contable_id': anticipo.categoria_contable.id if anticipo.categoria_contable else None,
                'categoria_contable_nombre': f"{anticipo.categoria_contable.codigo} - {anticipo.categoria_contable.nombre}" if anticipo.categoria_contable else '',
                'estado': anticipo.estado
            }

            print(f"[DEBUG] Centro costo ID: {anticipo_data['centro_costo_id']}")
            print(f"[DEBUG] Categoria contable ID: {anticipo_data['categoria_contable_id']}")
            print(f"[DEBUG] Concepto: {anticipo_data['concepto']}")

            # Agregar las formas de pago con nombres completos
            formas_pago = FormaPago.objects.select_related('tipo', 'forma').filter(anticipo=anticipo)
            anticipo_data['formas_pago'] = []

            for fp in formas_pago:
                fp_data = {
                    'id': fp.id,
                    'tipo_id': fp.tipo.id if fp.tipo else None,
                    'tipo_nombre': fp.tipo.nombre if fp.tipo else 'N/A',
                    'forma_id': fp.forma.id if fp.forma else None,
                    'forma_nombre': fp.forma.nombre if fp.forma else 'N/A',
                    'valor': float(fp.valor),
                    'referencia': fp.referencia or '',
                    'banco': fp.banco or '',
                    'observacion': fp.observacion or ''
                }
                anticipo_data['formas_pago'].append(fp_data)
                print(f"[DEBUG] Forma de pago: {fp_data['forma_nombre']} - ${fp_data['valor']}")

            print(f"[DEBUG] Total formas de pago: {len(anticipo_data['formas_pago'])}")
            return anticipo_data

        except Anticipo.DoesNotExist:
            return {'error': 'Anticipo no encontrado'}
        except Exception as e:
            print(f"[DEBUG] Error en get_anticipo: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}

    def create_anticipo(self, request):
        """Crea un nuevo anticipo con sus formas de pago"""
        with transaction.atomic():
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

            # Convertir fecha de string a objeto date
            fecha_str = request.POST.get('fecha')
            if fecha_str and isinstance(fecha_str, str):
                anticipo.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            else:
                anticipo.fecha = fecha_str

            anticipo.monto = Decimal(request.POST.get('monto', 0))
            anticipo.concepto = request.POST.get('concepto', '')

            categoria_contable_id = request.POST.get('categoria_contable_id')
            if categoria_contable_id:
                anticipo.categoria_contable_id = categoria_contable_id

            anticipo.save()
            print(f"[DEBUG] Anticipo creado con ID: {anticipo.id}")

            # Guardar formas de pago
            formas_pago_json = request.POST.get('formas_pago', '[]')
            formas_pago_data = json.loads(formas_pago_json)

            for fp_data in formas_pago_data:
                forma_pago = FormaPago()
                forma_pago.anticipo = anticipo
                forma_pago.tipo_id = fp_data.get('tipo_id')
                forma_pago.forma_id = fp_data.get('forma_id')
                forma_pago.valor = Decimal(str(fp_data.get('valor', 0)))
                forma_pago.referencia = fp_data.get('referencia', '')
                forma_pago.banco = fp_data.get('banco', '')
                forma_pago.observacion = fp_data.get('observacion', '')
                forma_pago.save()

            # Generar asiento contable
            self.generar_asiento_contable(anticipo)

            return {
                'success': True,
                'message': 'Anticipo creado exitosamente',
                'anticipo': anticipo.toJSON()
            }

    def update_anticipo(self, request):
        """Actualiza un anticipo existente con sus formas de pago"""
        anticipo_id = request.POST.get('id')
        if not anticipo_id:
            return {'error': 'ID de anticipo no proporcionado'}

        with transaction.atomic():
            try:
                anticipo = Anticipo.objects.get(pk=anticipo_id)

                # Actualizar campos
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

                # Convertir fecha de string a objeto date
                fecha_str = request.POST.get('fecha')
                if fecha_str and isinstance(fecha_str, str):
                    anticipo.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                else:
                    anticipo.fecha = fecha_str

                anticipo.monto = Decimal(request.POST.get('monto', 0))
                anticipo.concepto = request.POST.get('concepto', '')

                categoria_contable_id = request.POST.get('categoria_contable_id')
                if categoria_contable_id:
                    anticipo.categoria_contable_id = categoria_contable_id

                anticipo.save()

                # Eliminar formas de pago anteriores
                FormaPago.objects.filter(anticipo=anticipo).delete()

                # Guardar nuevas formas de pago
                formas_pago_json = request.POST.get('formas_pago', '[]')
                formas_pago_data = json.loads(formas_pago_json)

                for fp_data in formas_pago_data:
                    forma_pago = FormaPago()
                    forma_pago.anticipo = anticipo
                    forma_pago.tipo_id = fp_data.get('tipo_id')
                    forma_pago.forma_id = fp_data.get('forma_id')
                    forma_pago.valor = Decimal(str(fp_data.get('valor', 0)))
                    forma_pago.referencia = fp_data.get('referencia', '')
                    forma_pago.banco = fp_data.get('banco', '')
                    forma_pago.observacion = fp_data.get('observacion', '')
                    forma_pago.save()

                # Regenerar asiento contable
                from app_contabilidad_planCuentas.models import EncabezadoCuentasPlanCuenta
                EncabezadoCuentasPlanCuenta.objects.filter(comprobante=f"ANT-{anticipo.id}").delete()
                self.generar_asiento_contable(anticipo)

                return {
                    'success': True,
                    'message': 'Anticipo actualizado exitosamente',
                    'anticipo': anticipo.toJSON()
                }
            except Anticipo.DoesNotExist:
                return {'error': 'Anticipo no encontrado'}

    def generar_asiento_contable(self, anticipo):
        """
        Genera el asiento contable del anticipo
        DEBE: Cuenta de anticipo (2.1.1.04 - Anticipos a clientes/proveedores)
        HABER: Cuenta de efectivo/banco según forma de pago
        """
        from app_contabilidad_planCuentas.models import (
            EncabezadoCuentasPlanCuenta,
            DetalleCuentasPlanCuenta,
            PlanCuenta
        )
        from django.utils import timezone

        print(f"\n{'=' * 60}")
        print(f"[CONTABILIDAD] GENERANDO ASIENTO CONTABLE ANTICIPO #{anticipo.id}")
        print(f"{'=' * 60}")

        try:
            empresa = anticipo.centro_costo
            if not empresa:
                print("[CONTABILIDAD] ERROR: No hay empresa asignada")
                return None

            print(f"[CONTABILIDAD] Empresa: {empresa.siglas}")
            print(f"[CONTABILIDAD] Cliente/Proveedor: {anticipo.razon_social}")
            print(f"[CONTABILIDAD] Monto: ${anticipo.monto}")

            # Cuenta de anticipo (DEBE)
            cuenta_anticipo = anticipo.categoria_contable
            if not cuenta_anticipo:
                print("[CONTABILIDAD] ERROR: No hay cuenta contable asignada")
                return None

            print(f"[CONTABILIDAD] Cuenta anticipo: {cuenta_anticipo.codigo} - {cuenta_anticipo.nombre}")

            # Crear encabezado del asiento
            encabezado = EncabezadoCuentasPlanCuenta.objects.create(
                codigo=int(datetime.now().timestamp()),
                tip_cuenta='1',
                tip_transa='ANTICIPO',
                fecha=anticipo.fecha or timezone.now().date(),
                comprobante=f"ANT-{anticipo.id}",
                descripcion=f"Anticipo a {anticipo.razon_social} - {anticipo.concepto}",
                empresa=empresa,
                reg_control='RT'
            )

            print(f"[CONTABILIDAD] Encabezado creado ID: {encabezado.id}, Comprobante: {encabezado.comprobante}")

            # DEBE: Cuenta de anticipo
            detalle_debe = DetalleCuentasPlanCuenta.objects.create(
                encabezadocuentaplan=encabezado,
                orden=1,
                cuenta=cuenta_anticipo,
                detalle=f"Anticipo {anticipo.tipo_cliente.lower()}: {anticipo.razon_social}",
                debe=float(anticipo.monto),
                haber=0.00,
                origen='ANTICIPO'
            )
            print(f"[CONTABILIDAD] DEBE: {cuenta_anticipo.codigo} - ${detalle_debe.debe:.2f}")

            # HABER: Cuentas de efectivo/banco según formas de pago
            formas_pago = FormaPago.objects.select_related('forma').filter(anticipo=anticipo)
            orden = 2

            for fp in formas_pago:
                cuenta_haber = None
                forma_nombre = fp.forma.nombre.upper() if fp.forma else ''

                # Determinar la cuenta según la forma de pago
                if forma_nombre in ['EFECTIVO', 'CAJA']:
                    # Buscar cuenta de caja
                    cuenta_haber = PlanCuenta.objects.filter(
                        empresa=empresa,
                        codigo__icontains='1.1.1.01',
                        estado=True
                    ).first()
                    print(f"[CONTABILIDAD] Buscando cuenta de CAJA (1.1.1.01)")

                elif forma_nombre in ['CHEQUE', 'TRANSFERENCIA', 'DEPOSITO', 'TRANSFERENCIA BANCARIA']:
                    # Buscar cuenta de banco
                    if fp.banco:
                        cuenta_haber = PlanCuenta.objects.filter(
                            empresa=empresa,
                            nombre__icontains=fp.banco,
                            codigo__istartswith='1.1.1.02',
                            estado=True
                        ).first()
                        print(f"[CONTABILIDAD] Buscando cuenta de BANCO: {fp.banco}")

                    if not cuenta_haber:
                        cuenta_haber = PlanCuenta.objects.filter(
                            empresa=empresa,
                            codigo__istartswith='1.1.1.02',
                            estado=True
                        ).first()
                        print(f"[CONTABILIDAD] Usando cuenta genérica de bancos (1.1.1.02)")

                if not cuenta_haber:
                    # Fallback: usar caja general
                    cuenta_haber = PlanCuenta.objects.filter(
                        empresa=empresa,
                        codigo__icontains='1.1.1',
                        estado=True
                    ).first()
                    print(f"[CONTABILIDAD] FALLBACK: Usando cuenta genérica (1.1.1)")

                if cuenta_haber:
                    detalle_haber = DetalleCuentasPlanCuenta.objects.create(
                        encabezadocuentaplan=encabezado,
                        orden=orden,
                        cuenta=cuenta_haber,
                        detalle=f"{forma_nombre} - {fp.referencia or 'S/N'}",
                        debe=0.00,
                        haber=float(fp.valor),
                        origen='ANTICIPO'
                    )
                    print(f"[CONTABILIDAD] HABER: {cuenta_haber.codigo} - ${detalle_haber.haber:.2f}")
                    orden += 1
                else:
                    print(f"[CONTABILIDAD] ERROR: No se encontró cuenta para {forma_nombre}")

            print(f"{'=' * 60}")
            print(f"[CONTABILIDAD] ASIENTO CREADO EXITOSAMENTE")
            print(f"[CONTABILIDAD] Comprobante: {encabezado.comprobante}")
            print(f"{'=' * 60}\n")

            return encabezado

        except Exception as e:
            print(f"{'=' * 60}")
            print(f"[CONTABILIDAD] ERROR CRÍTICO AL GENERAR ASIENTO")
            print(f"[CONTABILIDAD] Error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"{'=' * 60}\n")
            return None

    def get_plan_cuentas(self, request):
        """Obtiene el plan de cuentas filtrado por empresa"""
        empresa_id = request.POST.get('empresa_id')

        if not empresa_id:
            print("[DEBUG] No se proporcionó empresa_id")
            return []

        print(f"[DEBUG] Buscando plan de cuentas para empresa_id: {empresa_id}")

        # Buscar cuentas con diferentes estrategias
        cuentas = PlanCuenta.objects.filter(
            estado=True,
            empresa_id=empresa_id,
            codigo__icontains='2.1.1.04'
        )

        print(f"[DEBUG] Cuentas con código 2.1.1.04: {cuentas.count()}")

        if not cuentas.exists():
            print("[DEBUG] Buscando con código alternativo 2.1.1")
            cuentas = PlanCuenta.objects.filter(
                estado=True,
                empresa_id=empresa_id,
                codigo__istartswith='2.1.1'
            )
            print(f"[DEBUG] Cuentas con código 2.1.1: {cuentas.count()}")

        if not cuentas.exists():
            print("[DEBUG] Buscando con código alternativo 2.1")
            cuentas = PlanCuenta.objects.filter(
                estado=True,
                empresa_id=empresa_id,
                codigo__istartswith='2.1'
            )
            print(f"[DEBUG] Cuentas con código 2.1: {cuentas.count()}")

        if not cuentas.exists():
            print("[DEBUG] Mostrando todas las cuentas de la empresa")
            cuentas = PlanCuenta.objects.filter(
                estado=True,
                empresa_id=empresa_id
            )
            print(f"[DEBUG] Total de cuentas de la empresa: {cuentas.count()}")

        cuentas = cuentas.order_by('codigo')

        resultado = [
            {
                'id': c.id,
                'codigo': c.codigo,
                'nombre': c.nombre,
                'descripcion': f"{c.codigo} - {c.nombre}"
            }
            for c in cuentas
        ]

        print(f"[DEBUG] Retornando {len(resultado)} cuentas")
        return resultado


class AnticipoListView(TemplateView):
    template_name = 'app_anticipos/anticipo_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestión de Anticipos'
        context['empresas'] = Empresa.objects.filter(estado=True)
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
            elif action == 'delete':
                data = self.delete_anticipo(request)
            else:
                data['error'] = 'Acción no válida'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def list_anticipos(self, request):
        anticipos = Anticipo.objects.select_related('centro_costo', 'categoria_contable').all()

        empresa_id = request.POST.get('empresa_id')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        if empresa_id:
            anticipos = anticipos.filter(centro_costo_id=empresa_id)
        if fecha_inicio and fecha_fin:
            anticipos = anticipos.filter(fecha__range=[fecha_inicio, fecha_fin])

        return [anticipo.toJSON() for anticipo in anticipos]

    def delete_anticipo(self, request):
        anticipo_id = request.POST.get('id')
        anticipo = Anticipo.objects.get(pk=anticipo_id)
        anticipo.estado = False
        anticipo.save()
        return {'success': True, 'message': 'Anticipo eliminado exitosamente'}


class TipoPagoListView(TemplateView):
    template_name = 'app_anticipos/tipo_pago_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Tipos de Pago'
        context['tipos_pago'] = TipoPago.objects.all()
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
    template_name = 'app_anticipos/forma_pago_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Formas de Pago'
        context['formas_pago'] = FormaPagoOpcion.objects.all()
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