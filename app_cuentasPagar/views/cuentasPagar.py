import json
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, FormView
from app_venta.forms import DebtsPay, PaymentsDebtsPay
from app_cuentasPagar.forms import PaymentsDebtsPayForm
from app_reportes.forms import ReportForm


class DebtsPayListView( FormView):
    template_name = 'app_cuentasPagar/list.html'
    form_class = ReportForm

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                data = []
                queryset = DebtsPay.objects.filter()
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                if len(start_date) and len(end_date):
                    queryset = queryset.filter(date_joined__range=[start_date, end_date])
                for i in queryset:
                    data.append(i.toJSON())
            elif action == 'search_pays':
                data = []
                for count, i in enumerate(PaymentsDebtsPay.objects.filter(debts_pay_id=request.POST['id']).order_by('id')):
                    item = i.toJSON()
                    item['index'] = count + 1
                    data.append(item)
            elif action == 'delete_pay':
                id = request.POST['id']
                payment = PaymentsDebtsPay.objects.get(pk=id)
                debtspay = payment.debts_pay
                payment.delete()
                debtspay.validate_debt()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Cuentas por Pagar'
        context['create_url'] = reverse_lazy('debts_pay_create')
        return context


class DebtsPayCreateView(CreateView):
    model = DebtsPay
    template_name = 'debts_pay/create.html'
    form_class = PaymentsDebtsPayForm
    success_url = reverse_lazy('debts_pay_list')

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search_debts_pay':
                data = []
                term = request.POST['term']
                for i in DebtsPay.objects.filter(Q(purchase__provider__name__icontains=term) | Q(purchase__number__icontains=term)).exclude(state=False)[0:10]:
                    item = i.toJSON()
                    item['text'] = i.get_full_name()
                    data.append(item)
            elif action == 'add':
                with transaction.atomic():
                    payment = PaymentsDebtsPay()
                    payment.debts_pay_id = int(request.POST['debts_pay'])
                    payment.date_joined = request.POST['date_joined']
                    payment.valor = float(request.POST['valor'])
                    payment.description = request.POST['description']
                    payment.save()
                    payment.debts_pay.validate_debt()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Nuevo registro de un Pago'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context


class DebtsPayDeleteView(DeleteView):
    model = DebtsPay
    template_name = 'delete.html'
    success_url = reverse_lazy('debts_pay_list')

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
