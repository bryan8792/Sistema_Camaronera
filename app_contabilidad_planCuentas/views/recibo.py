import json
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from app_contabilidad_planCuentas.models import Recibo
from app_contabilidad_planCuentas.forms import ReciboForm

class ReceiptListView(TemplateView):
    template_name = 'app_contabilidad_planCuentas/recibo/recibo_listar.html'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                data = []
                for i in Recibo.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Comprobantes'
        context['create_url'] = reverse_lazy('app_planCuentas:recibo_crear')
        return context


class ReceiptCreateView(CreateView):
    model = Recibo
    form_class = ReciboForm
    template_name = 'app_contabilidad_planCuentas/recibo/recibo_crear.html'
    success_url = reverse_lazy('app_planCuentas:recibo_listar')
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'create':
                data = self.get_form().save()
            elif action == 'validate_data':
                data = {'valid': True}
                queryset = Recibo.objects.all()
                voucher_type = request.POST.get('voucher_type')
                establishment_code = request.POST.get('establishment_code')
                issuing_point_code = request.POST.get('issuing_point_code')
                empresa_id = request.POST.get('empresa_id')
                if all([voucher_type, establishment_code, issuing_point_code, empresa_id]):
                    existe = queryset.filter(
                        voucher_type=voucher_type,
                        establishment_code=establishment_code,
                        issuing_point_code=issuing_point_code,
                        empresa_id=empresa_id
                    ).exists()
                    if existe:
                        data['valid'] = False
                        data['error'] = "El comprobante ya se encuentra registrado para esta empresa."
                else:
                    data['valid'] = False
                    data['error'] = "Datos incompletos para validar."
            else:
                data['error'] = "No ha seleccionado ninguna opción."
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Nuevo registro de un Comprobante'
        context['list_url'] = self.success_url
        context['action'] = 'create'
        return context


class ReceiptUpdateView(UpdateView):
    model = Recibo
    template_name = 'app_contabilidad_planCuentas/recibo/recibo_crear.html'
    form_class = ReciboForm
    success_url = reverse_lazy('app_planCuentas:recibo_listar')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'edit':
                data = self.get_form().save()
            elif action == 'validate_data':
                data = {'valid': True}
                queryset = Recibo.objects.all().exclude(id=self.object.id)
                voucher_type = request.POST['voucher_type']
                establishment_code = request.POST['establishment_code']
                issuing_point_code = request.POST['issuing_point_code']
                if len(voucher_type) and len(issuing_point_code) and len(establishment_code):
                    data['valid'] = not queryset.filter(voucher_type=voucher_type, establishment_code=establishment_code, issuing_point_code=issuing_point_code).exists()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Edición de un Comprobante'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        return context


class ReceiptDeleteView(DeleteView):
    model = Recibo
    template_name = 'app_contabilidad_planCuentas/recibo/recibo_crear.html'
    success_url = reverse_lazy('app_planCuentas:recibo_listar')

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context
