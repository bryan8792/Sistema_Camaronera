import json
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import View
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from Sistema_Camaronera import settings
from cliente.forms import ClienteUserForm, Cliente
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
        try:
            data = Cliente.objects.get(pk=request.POST['id']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # pongo el titulo a mi tabla y demas que necesiten
        context['nombre'] = 'Listado de Clientes'
        return context


# class ClienteCreateView(CreateView):
#     model = Cliente
#     form_class = ClienteUserForm
#     template_name = 'app_cliente/cliente_crear.html'
#     success_url = reverse_lazy('app_cliente:listar_cliente')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['nombre'] = 'Registrar nuevo Cliente'
#         context['entity'] = 'Cliente'
#         context['action'] = 'crear'
#         return context


class ClienteCreateView(View):
    template_name = 'app_cliente/cliente_crear.html'
    success_url = reverse_lazy('app_cliente:listar_cliente')

    def get(self, request):
        user_form = ClienteUserForm()
        cliente_form = Cliente()
        context = {
            'user_form': user_form,
            'form': cliente_form,
            'nombre': 'Registrar nuevo Cliente',
            'entity': 'Cliente',
            'action': 'crear',
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user_form = ClienteUserForm(request.POST)
        cliente_form = Cliente(request.POST)
        if user_form.is_valid() and cliente_form.is_valid():
            # Guardar el usuario primero
            user = user_form.save(commit=False)
            # Por ejemplo, si tienes password en user_form, haz: user.set_password(...)
            user.save()

            # Guardar el cliente con el usuario asignado
            cliente = cliente_form.save(commit=False)
            cliente.usuario = user
            cliente.save()

            return redirect(self.success_url)

        context = {
            'user_form': user_form,
            'form': cliente_form,
            'nombre': 'Registrar nuevo Cliente',
            'entity': 'Cliente',
            'action': 'crear',
        }
        return render(request, self.template_name, context)


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteUserForm
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
    form_class = ClienteUserForm
    template_name = 'app_cliente/cliente_eliminar.html'
    success_url = reverse_lazy('app_cliente:listar_cliente')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Cliente'
        context['entity'] = 'Cliente'
        context['action'] = 'delete'
        return context
