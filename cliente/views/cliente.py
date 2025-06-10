import json
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from Sistema_Camaronera import settings
from cliente.forms import ClientForm, Cliente
from utilities.sri import SRI
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class ClienteListView(TemplateView):
    model = Cliente
    template_name = 'app_cliente/cliente_listar.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                data = []
                for i in Cliente.objects.filter():
                    data.append(i.toJSON())
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Clientes'
        context['nombre'] = 'Listado de Clientes'
        # context['create_url'] = reverse_lazy('client_create')
        return context


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClientForm
    template_name = 'app_cliente/cliente_crear.html'
    success_url = reverse_lazy('app_cliente:listar_cliente')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Ingresar Categoría'
        context['entity'] = 'Categoría'
        context['action'] = 'crear'
        return context


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClientForm
    template_name = 'app_cliente/cliente_crear.html'
    success_url = reverse_lazy('app_cliente:listar_cliente')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Cliente'
        context['entity'] = 'Cliente'
        context['action'] = 'edit'
        return context


class ClienteDeleteView(DeleteView):
    model = Cliente
    form_class = ClientForm
    template_name = 'app_cliente/cliente_eliminar.html'
    success_url = reverse_lazy('app_cliente:listar_cliente')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Cliente'
        context['entity'] = 'Cliente'
        context['action'] = 'delete'
        return context
