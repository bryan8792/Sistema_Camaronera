import json
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, FormView
from app_reportes.forms import ReportForm
from app_cuentasCobrar.forms import PaymentsCtaCollectForm
from app_venta.models import CtasCollect, PaymentsCtaCollect


class CtasCollectListView(FormView):
    template_name = 'app_cuentasCobrar/list.html'
    form_class = ReportForm

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                data = []
                queryset = CtasCollect.objects.filter()
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                if len(start_date) and len(end_date):
                    queryset = queryset.filter(date_joined__range=[start_date, end_date])
                for i in queryset:
                    data.append(i.toJSON())
            elif action == 'search_pays':
                data = []
                for count, i in enumerate(PaymentsCtaCollect.objects.filter(ctas_collect_id=request.POST['id']).order_by('id')):
                    item = i.toJSON()
                    item['index'] = count + 1
                    data.append(item)
            elif action == 'delete_pay':
                id = request.POST['id']
                payment = PaymentsCtaCollect.objects.get(pk=id)
                ctascollect = payment.ctas_collect
                payment.delete()
                ctascollect.validate_debt()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Cuentas por Cobrar'
        context['nombre'] = 'Cuentas por Cobrar'
        context['create_url'] = reverse_lazy('ctas_collect_create')
        return context


class CtasCollectCreateView(CreateView):
    model = CtasCollect
    template_name = 'app_cuentasCobrar/create.html'
    form_class = PaymentsCtaCollectForm
    success_url = reverse_lazy('ctas_collect_list')
    permission_required = 'add_ctas_collect'

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search_ctas_collect':
                data = []
                term = request.POST['term']
                for i in CtasCollect.objects.filter(Q(sale__client__user__names__icontains=term) | Q(sale__client__dni__icontains=term)).exclude(state=False)[0:10]:
                    item = i.toJSON()
                    item['text'] = i.get_full_name()
                    data.append(item)
            elif action == 'add':
                with transaction.atomic():
                    payment = PaymentsCtaCollect()
                    payment.ctas_collect_id = int(request.POST['ctas_collect'])
                    payment.date_joined = request.POST['date_joined']
                    payment.valor = float(request.POST['valor'])
                    payment.description = request.POST['description']
                    payment.save()
                    payment.ctas_collect.validate_debt()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Nuevo registro de un Pago'
        context['nombre'] = 'Cuentas por Cobrar'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context


class CtasCollectDeleteView(DeleteView):
    model = CtasCollect
    template_name = 'app_cuentasCobrar/delete.html'
    success_url = reverse_lazy('ctas_collect_list')
    permission_required = 'delete_ctas_collect'

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
