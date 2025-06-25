
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import *
from app_user.forms import GroupForm
from app_user.models import GrupoModulo
from app_user.forms import UserForm
from app_user.models import User
from app_user.forms import ModuloForm, TipoModuloForm
from app_user.models import Modulo, TipoModulo


class crearUsuarioView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'app_user/user_crear.html'
    success_url = reverse_lazy('app_usuario:listar_usuario')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.groups.set(form.cleaned_data['groups'])
        self.object.user_permissions.set(form.cleaned_data['user_permissions'])
        return response

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

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.groups.set(form.cleaned_data['groups'])
        self.object.user_permissions.set(form.cleaned_data['user_permissions'])
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Usuario'
        context['entity'] = 'Usuario'
        context['action'] = 'editar'
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


class detalleUsuarioView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'app_user/user_detail.html'
    context_object_name = 'usuario'


class crearGrupoView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'app_user/group_crear.html'
    success_url = reverse_lazy('app_usuario:listar_grupo')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Asignar módulos al grupo
        modulos = form.cleaned_data.get('modulos', [])
        for modulo in modulos:
            GrupoModulo.objects.get_or_create(grupo=self.object, modulo=modulo)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Crear Grupo'
        context['entity'] = 'Grupo'
        context['action'] = 'crear'
        return context


class actualizarGrupoView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'app_user/group_crear.html'
    success_url = reverse_lazy('app_usuario:listar_grupo')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Actualizar módulos del grupo
        GrupoModulo.objects.filter(grupo=self.object).delete()
        modulos = form.cleaned_data.get('modulos', [])
        for modulo in modulos:
            GrupoModulo.objects.create(grupo=self.object, modulo=modulo)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Grupo'
        context['entity'] = 'Grupo'
        context['action'] = 'editar'
        return context


class eliminarGrupoView(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = 'app_user/group_eliminar.html'
    success_url = reverse_lazy('app_usuario:listar_grupo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Grupo'
        context['entity'] = 'Grupo'
        return context


class listarGrupoView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'app_user/group_listar.html'

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
                for grupo in Group.objects.all():
                    item = {
                        'id': grupo.id,
                        'name': grupo.name,
                        'permissions_count': grupo.permissions.count(),
                        'users_count': grupo.user_set.count(),
                        'modulos': [gm.modulo.nombre for gm in GrupoModulo.objects.filter(grupo=grupo)]
                    }
                    data.append(item)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Grupos'
        return context


class detalleGrupoView(LoginRequiredMixin, DetailView):
    model = Group
    template_name = 'app_user/group_detail.html'
    context_object_name = 'grupo'


class crearModuloView(LoginRequiredMixin, CreateView):
    model = Modulo
    form_class = ModuloForm
    template_name = 'app_user/modulo_crear.html'
    success_url = reverse_lazy('app_usuario:listar_modulo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Crear Módulo'
        context['entity'] = 'Módulo'
        context['action'] = 'crear'
        return context


class actualizarModuloView(LoginRequiredMixin, UpdateView):
    model = Modulo
    form_class = ModuloForm
    template_name = 'app_user/modulo_crear.html'
    success_url = reverse_lazy('app_usuario:listar_modulo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Módulo'
        context['entity'] = 'Módulo'
        context['action'] = 'editar'
        return context


class eliminarModuloView(LoginRequiredMixin, DeleteView):
    model = Modulo
    template_name = 'app_user/modulo_eliminar.html'
    success_url = reverse_lazy('app_usuario:listar_modulo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Módulo'
        context['entity'] = 'Módulo'
        return context


class listarModuloView(LoginRequiredMixin, ListView):
    model = Modulo
    template_name = 'app_user/modulo_listar.html'

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
                for modulo in Modulo.objects.all():
                    item = modulo.toJSON()
                    data.append(item)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Módulos'
        return context


# Vistas para Tipo de Módulo
class crearTipoModuloView(LoginRequiredMixin, CreateView):
    model = TipoModulo
    form_class = TipoModuloForm
    template_name = 'app_user/tipo_modulo_crear.html'
    success_url = reverse_lazy('app_usuario:listar_tipo_modulo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Crear Tipo de Módulo'
        context['entity'] = 'Tipo de Módulo'
        context['action'] = 'crear'
        return context


class listarTipoModuloView(LoginRequiredMixin, ListView):
    model = TipoModulo
    template_name = 'app_user/tipo_modulo_listar.html'

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
                for tipo in TipoModulo.objects.all():
                    item = tipo.toJSON()
                    data.append(item)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Tipos de Módulos'
        return context