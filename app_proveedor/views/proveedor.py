from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from app_contabilidad_planCuentas.forms import PlanCuentaForm
from app_contabilidad_planCuentas.models import PlanCuenta
from app_proveedor.forms import ProveedorForm
from app_proveedor.models import Proveedor


class crearProveedorView(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'app_proveedor/proveedor_crear.html'
    success_url = reverse_lazy('app_proveedor:listar_proveedor')
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_clients':
                print('LLEGO AQUI A SEARCH CUENTA DEL PLAN')
                data = []
                term = request.POST['term']
                clients = PlanCuenta.objects.filter(Q(codigo__exact=term) | Q(nombre__icontains=term))[0:10]
                for i in clients:
                    item = i.toJSON()
                    item['text'] = i.get_full_name()
                    data.append(item)

            elif action == 'create_client':
                with transaction.atomic():
                    frmClient = PlanCuentaForm(request.POST)
                    if frmClient.is_valid():
                        plan = frmClient.save()
                        data = plan.toJSON()
                        data['message'] = 'Plan de cuenta creado exitosamente'
                    else:
                        data['error'] = frmClient.errors

            elif action == 'create':
                print('LLEGÓ A CREATE')
                # Procesa los datos enviados para crear un nuevo proveedor
                form = self.form_class(request.POST)
                if form.is_valid():
                    proveedor = form.save()
                    data['message'] = 'Proveedor creado exitosamente'
                    data['id'] = proveedor.id
                    return redirect(self.success_url)
                else:
                    context = self.get_context_data()
                    context['form'] = form
                    return render(request, self.template_name, context)

            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Formulario de Registro de Proveedor'
        context['frmPlan'] = PlanCuentaForm()
        # context['list_url'] = self.success_url
        context['entity'] = 'Llego valor'
        context['action'] = 'create'
        context['estado_activo'] = False
        return context


class actualizarProveedorView(UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'app_proveedor/proveedor_crear.html'
    success_url = reverse_lazy('app_proveedor:listar_proveedor')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        if action == 'edit':
            form = self.form_class(request.POST, instance=self.get_object())
            if form.is_valid():
                form.save()
                return redirect(self.success_url)
            else:
                context = self.get_context_data()
                context['form'] = form
                return render(request, self.template_name, context)
        else:
            return JsonResponse({'error': 'Acción inválida'}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Formulario de Actualización de Proveedor'
        context['frmPlan'] = PlanCuentaForm()
        # context['list_url'] = self.success_url
        context['entity'] = 'Llego valor'
        context['action'] = 'edit'
        context['estado_activo'] = 'true'
        return context


class eliminarProveedorView(DeleteView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'app_proveedor/proveedor_eliminar.html'
    success_url = reverse_lazy('app_proveedor:listar_proveedor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Proveedor'
        return context


class listarProveedorView(ListView):
    model = Proveedor
    template_name = 'app_proveedor/proveedor_listar.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Proveedor.objects.get(pk=request.POST['id']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Proveedores'
        context['proveedor'] = Proveedor.objects.all()
        return context


