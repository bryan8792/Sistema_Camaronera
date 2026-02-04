# app_retencion/views/retencion.py
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import json, os
from django.conf import settings
from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from app_retencion.models import Retention, RetentionDetail
from app_empresa.app_reg_empresa.models import Empresa
from app_proveedor.models import Proveedor
from app_contabilidad_planCuentas.models import Recibo
from utilities.sri import SRI


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
                retention = Retention.objects.create(
                    company_id=request.POST.get('company'),
                    provider_id=request.POST.get('provider') or None,
                    receipt_id=request.POST.get('receipt') or None,
                    voucher_number=request.POST.get('voucher_number', ''),
                    voucher_number_full=request.POST.get('voucher_number_full', ''),
                )

                details = request.POST.getlist('details[]')
                for d in details:
                    if not d:
                        continue
                    data = json.loads(d)
                    if isinstance(data, dict):
                        data = [data]

                    for item in data:
                        # Validar y limpiar el campo numero_15_digitos
                        numero_15_digitos = item.get('numero_15_digitos', '')
                        if numero_15_digitos:
                            # Asegurar que solo sean números y máximo 15 dígitos
                            numero_15_digitos = ''.join(filter(str.isdigit, str(numero_15_digitos)))[:15]

                        # Validar el campo comp_pago_cuota
                        comp_pago_cuota = item.get('comp_pago_cuota', '')
                        # Si no viene, asignar un valor por defecto
                        if not comp_pago_cuota:
                            comp_pago_cuota = 'OPCION_1'  # O el valor por defecto que prefieras

                        # Crear el detalle con los nuevos campos
                        RetentionDetail.objects.create(
                            retention=retention,
                            tax_type=item.get('tax_type', 'IVA'),
                            tax_code=item.get('tax_code', ''),
                            numero_15_digitos=numero_15_digitos,  # Nuevo campo
                            comp_pago_cuota=comp_pago_cuota,  # Nuevo campo
                            percentage=Decimal(str(item.get('percentage', 0))),
                            base=Decimal(str(item.get('base', 0))),
                        )

                retention.update_totals()
                retention.save_pdf_authorized()

                xml_dir = os.path.join(settings.MEDIA_ROOT, 'retenciones')
                os.makedirs(xml_dir, exist_ok=True)
                xml_path = os.path.join(xml_dir, f"retention_{retention.id}.xml")
                retention.generate_xml(xml_path)

                response['success'] = True
                response['pdf_url'] = retention.pdf_authorized.url
                response['xml_url'] = settings.MEDIA_URL + f"retenciones/retention_{retention.id}.xml"

        except Exception as e:
            response['error'] = str(e)

        return JsonResponse(response)


@method_decorator(csrf_exempt, name='dispatch')
class RetentionListView(ListView):
    model = Retention
    template_name = 'app_retencion/admin/list.html'

    def post(self, request, *args, **kwargs):
        print('POST ACTION:', request.POST.get('action'))
        action = request.POST.get('action')
        data = {}

        try:
            # ================= LISTADO =================
            if action == 'searchdata':
                data = []
                for r in Retention.objects.select_related('company', 'provider'):
                    data.append({
                        'id': r.id,
                        'voucher_number_full': r.voucher_number_full,
                        'provider': r.provider.razon_soc if r.provider else '',
                        'date_joined': r.date_joined.strftime('%d/%m/%Y'),
                        'total_retained': f'{r.total_retained:.2f}',
                        'pdf': r.pdf_authorized.url if r.pdf_authorized else '',
                        'xml': f'/media/retenciones/retention_{r.id}.xml',
                        'email_sent': r.email_sent,
                    })

            # ================= ENVIAR EMAIL =================
            elif action == 'send_retention_by_email':
                retention = Retention.objects.get(pk=request.POST.get('id'))

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


