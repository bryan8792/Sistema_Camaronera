
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from app_user.forms import UserForm
from app_user.models import User


class crearUsuarioView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'app_user/user_crear.html'
    success_url = reverse_lazy('app_usuario:listar_usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Ingresar Usuario'
        context['entity'] = 'Usuario'
        context['action'] = 'crear'
        return context


class actualizarUsuarioView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'app_user/user_crear.html'
    success_url = reverse_lazy('app_usuario:listar_usuario')

    def dispatch(self, request, *args, **kwargs):
        return  super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Usuario'
        context['entity'] = 'Usuario'
        context['action'] = 'crear'
        return context


class eliminarUsuarioView(DeleteView):
    model = User
    form_class = UserForm
    template_name = 'app_user/user_eliminar.html'
    success_url = reverse_lazy('app_usuario:listar_usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Usuario'
        context['entity'] = 'Usuario'
        context['action'] = 'crear'
        return context


#CREAREMOS LISTA BASADA EN CLASES
class listarUsuarioView(ListView):
    model = User
    # defino la plantilla
    template_name = 'app_user/user_listar.html'


    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in User.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #pongo el titulo a mi tabla y demas que necesiten
        context['nombre'] = 'Usuario'
        return context