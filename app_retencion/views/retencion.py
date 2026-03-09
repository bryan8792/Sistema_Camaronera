from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import json

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from app_retencion.models import Retention, RetentionDetail
from app_empresa.app_reg_empresa.models import Empresa
from app_proveedor.models import Proveedor
from app_contabilidad_planCuentas.models import Recibo
from utilities.sri import SRI


# ======================================================
# CREAR RETENCIÓN + FLUJO SRI REAL
# ======================================================
class RetentionCreateView(CreateView):
    model = Retention
    template_name = 'app_retencion/admin/create.html'
    success_url = reverse_lazy('app_retencion:retention_list')
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = Empresa.objects.all()
        context['providers'] = Proveedor.objects.all()
        context['receipts'] = Recibo.objects.filter(voucher_type='07')
        return context

    def post(self, request, *args, **kwargs):
        response = {}

        try:
            with transaction.atomic():

                # ================= CREAR RETENCIÓN =================
                retention = Retention.objects.create(
                    company_id=request.POST.get('company'),
                    provider_id=request.POST.get('provider') or None,
                    receipt_id=request.POST.get('receipt') or None,
                )

                # ================= DETALLES =================
                details = request.POST.getlist('details[]')
                if not details:
                    raise Exception('Debe ingresar al menos un detalle')

                for d in details:
                    if not d:
                        continue

                    data = json.loads(d)
                    if isinstance(data, dict):
                        data = [data]

                    for item in data:
                        RetentionDetail.objects.create(
                            retention=retention,
                            tax_type=item.get('tax_type', 'IVA'),
                            tax_code=item.get('tax_code', ''),
                            numero_15_digitos=str(item.get('numero_15_digitos', ''))[:15],
                            comp_pago_cuota=item.get('comp_pago_cuota') or 'OPCION_1',
                            percentage=Decimal(str(item.get('percentage', 0))),
                            base=Decimal(str(item.get('base', 0))),
                        )

                retention.update_totals()

                # Validar que existan detalles válidos
                if retention.details.count() == 0:
                    raise Exception('Debe ingresar al menos un detalle válido')

                retention.update_totals()

                # ================= VALIDACIONES =================
                if not retention.provider:
                    raise Exception('Debe seleccionar proveedor')

                if not retention.provider.ruc:
                    raise Exception('Proveedor sin identificación')

                # ================= FLUJO SRI REAL =================
                sri = SRI()

                # 1️⃣ Crear XML
                resp = sri.create_xml(retention)
                if not resp.get('resp'):
                    raise Exception(resp.get('error', 'Error al crear XML'))

                # 2️⃣ Firmar XML
                resp = sri.firm_xml(retention, resp['xml'])
                if not resp.get('resp'):
                    raise Exception(resp.get('error', 'Error al firmar XML'))

                # 3️⃣ Validar XML
                resp = sri.validate_xml(retention, resp['xml'])
                if not resp.get('resp'):
                    raise Exception(resp.get('error', 'XML rechazado por el SRI'))

                # 4️⃣ Autorizar XML
                resp = sri.authorize_xml(retention)
                if not resp.get('resp'):
                    raise Exception(resp.get('error', 'Comprobante NO autorizado'))

                # 5️⃣ Generar PDF autorizado
                retention.save_pdf_authorized()

                response['success'] = True
                response['message'] = 'Retención AUTORIZADA correctamente por el SRI'
                response['pdf_url'] = (retention.pdf_authorized.url if retention.pdf_authorized else '')

        except Exception as e:
            transaction.set_rollback(True)
            response['success'] = False
            response['error'] = str(e)

        return JsonResponse(response)


# ======================================================
# LISTADO + ENVÍO EMAIL
# ======================================================
@method_decorator(csrf_exempt, name='dispatch')
class RetentionListView(ListView):
    model = Retention
    template_name = 'app_retencion/admin/list.html'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        data = []

        try:
            # ================= LISTADO =================
            if action == 'searchdata':
                for r in Retention.objects.select_related('company', 'provider'):
                    data.append({
                        'id': r.id,
                        'voucher_number_full': r.voucher_number_full,
                        'provider': r.provider.razon_soc if r.provider else '',
                        'date_joined': r.date_joined.strftime('%d/%m/%Y'),
                        'total_retained': f'{r.total_retained:.2f}',
                        'pdf': r.pdf_authorized.url if r.pdf_authorized else '',
                        'xml': r.xml_authorized.url if hasattr(r, 'xml_authorized') and r.xml_authorized else '',
                        'email_sent': r.email_sent,
                    })

            # ================= ENVIAR EMAIL =================
            elif action == 'send_retention_by_email':
                retention = Retention.objects.get(pk=request.POST.get('id'))

                if not retention.pdf_authorized:
                    return JsonResponse({
                        'success': False,
                        'error': 'La retención aún no está autorizada'
                    })

                if not retention.provider or not retention.provider.mail:
                    return JsonResponse({
                        'success': False,
                        'error': 'El proveedor no tiene email registrado'
                    })

                sri = SRI()
                sri.notify_by_email(
                    instance=retention,
                    company=retention.company,
                    client=retention.provider
                )

                retention.email_sent = True
                retention.save(update_fields=['email_sent'])

                return JsonResponse({
                    'success': True,
                    'message': 'Comprobante enviado por correo correctamente'
                })

        except Exception as e:
            data = {'error': str(e)}

        return JsonResponse(data, safe=False)
