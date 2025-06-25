from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import *
from app_user.forms import GroupForm, CustomUserCreationForm
from app_user.models import GrupoModulo
from app_user.forms import UserForm
from app_user.models import User
from app_user.forms import ModuloForm, TipoModuloForm
from app_user.models import Modulo, TipoModulo


class crearUsuarioView(CreateView):
    model = User
    form_class = CustomUserCreationForm
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


# CREAREMOS LISTA BASADA EN CLASES
class listarUsuarioView(ListView):
    model = User
    # defino la plantilla
    template_name = 'app_user/user_listar.html'

    def user_to_json(self, user):
        """Método para convertir usuario a JSON de forma segura"""
        return {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Nunca',
            'groups_count': user.groups.count(),
            'permissions_count': user.user_permissions.count(),
        }

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
                    data.append(self.user_to_json(i))
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # defino el dicionario para enviar variables a mi plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # pongo el titulo a mi tabla y demas que necesiten
        context['nombre'] = 'Usuario'
        return context


class detalleUsuarioView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'app_user/user_detail.html'
    context_object_name = 'usuario'


class listarGrupoView(ListView):
    model = Group
    template_name = 'app_user/group_listar.html'
    context_object_name = 'grupos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Grupos'
        return context


class crearGrupoView(CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'app_user/group_crear.html'
    success_url = reverse_lazy('app_usuario:listar_grupo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Crear Grupo'
        context['modulos'] = Modulo.objects.all()  # Agregar módulos al contexto
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Grupo creado exitosamente.')
        return response


class actualizarGrupoView(UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'app_user/group_crear.html'
    success_url = reverse_lazy('app_usuario:listar_grupo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Grupo'
        context['modulos'] = Modulo.objects.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Grupo actualizado exitosamente.')
        return response


class eliminarGrupoView(DeleteView):
    model = Group
    template_name = 'app_user/group_eliminar.html'
    success_url = reverse_lazy('app_usuario:listar_grupo')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Grupo eliminado exitosamente.')
        return response


class detalleGrupoView(DetailView):
    model = Group
    template_name = 'app_user/group_detail.html'
    context_object_name = 'grupo'


class detalleModuloView(DetailView):
    model = Modulo
    template_name = 'app_user/modulo_detail.html'
    context_object_name = 'modulo'


class CrearTipoModuloView(LoginRequiredMixin, CreateView):
    model = TipoModulo
    form_class = TipoModuloForm
    template_name = 'app_user/tipo_modulo_crear.html'
    success_url = reverse_lazy('app_usuario:listar_tipo_modulo')

    def form_valid(self, form):
        messages.success(self.request, f'Tipo de módulo "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class ListarTipoModuloView(LoginRequiredMixin, ListView):
    model = TipoModulo
    template_name = 'app_user/tipo_modulo_listar.html'
    context_object_name = 'tipos_modulo'


class ListarTipoModuloAjaxView(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return self.handle_request(request)

    def post(self, request):
        return self.handle_request(request)

    def handle_request(self, request):
        try:
            tipos_modulo = TipoModulo.objects.all().order_by('nombre')

            data = []
            for tipo in tipos_modulo:
                data.append({
                    'id': tipo.id,
                    'nombre': tipo.nombre,
                    'descripcion': getattr(tipo, 'descripcion', '') or '',
                    'fecha_creacion': tipo.fecha_creacion.strftime('%d/%m/%Y %H:%M') if hasattr(tipo,
                                                                                                'fecha_creacion') else '',
                    'acciones': f'''
                        <div class="btn-group" role="group">
                            <a href="{reverse_lazy('app_usuario:editar_tipo_modulo', kwargs={'pk': tipo.id})}" class="btn btn-sm btn-warning" title="Editar">
                                <i class="fas fa-edit"></i>
                            </a>
                            <button class="btn btn-sm btn-danger" onclick="eliminarTipoModulo({tipo.id})" title="Eliminar">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    '''
                })

            return JsonResponse({
                'data': data,
                'recordsTotal': len(data),
                'recordsFiltered': len(data)
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'data': [],
                'recordsTotal': 0,
                'recordsFiltered': 0
            })


class EditarTipoModuloView(LoginRequiredMixin, UpdateView):
    model = TipoModulo
    form_class = TipoModuloForm
    template_name = 'app_user/tipo_modulo_editar.html'
    success_url = reverse_lazy('app_usuario:listar_tipo_modulo')

    def form_valid(self, form):
        messages.success(self.request, f'Tipo de módulo "{form.instance.nombre}" actualizado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class EliminarTipoModuloView(LoginRequiredMixin, DeleteView):
    model = TipoModulo
    template_name = 'app_user/tipo_modulo_eliminar.html'
    success_url = reverse_lazy('app_usuario:listar_tipo_modulo')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        messages.success(request, f'Tipo de módulo "{nombre}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# Vistas basadas en clases para Modulo
class CrearModuloView(LoginRequiredMixin, CreateView):
    model = Modulo
    form_class = ModuloForm
    template_name = 'app_user/modulo_crear.html'
    success_url = reverse_lazy('app_usuario:listar_modulo')

    def form_valid(self, form):
        messages.success(self.request, f'Módulo "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class ListarModuloView(LoginRequiredMixin, ListView):
    model = Modulo
    template_name = 'app_user/modulo_listar.html'
    context_object_name = 'modulos'


class ListarModuloAjaxView(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return self.handle_request(request)

    def post(self, request):
        return self.handle_request(request)

    def handle_request(self, request):
        try:
            modulos = Modulo.objects.select_related('tipo').all().order_by('nombre')

            data = []
            for modulo in modulos:
                data.append({
                    'id': modulo.id,
                    'nombre': modulo.nombre,
                    'tipo': modulo.tipo.nombre if modulo.tipo else 'Sin tipo',
                    'url': modulo.url or '',
                    'icono': modulo.icono or '',
                    'fecha_creacion': modulo.fecha_creacion.strftime('%d/%m/%Y %H:%M') if hasattr(modulo,
                                                                                                  'fecha_creacion') else '',
                    'acciones': f'''
                        <div class="btn-group" role="group">
                            <a href="{reverse_lazy('app_usuario:editar_modulo', kwargs={'pk': modulo.id})}" class="btn btn-sm btn-warning" title="Editar">
                                <i class="fas fa-edit"></i>
                            </a>
                            <button class="btn btn-sm btn-danger" onclick="eliminarModulo({modulo.id})" title="Eliminar">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    '''
                })

            return JsonResponse({
                'data': data,
                'recordsTotal': len(data),
                'recordsFiltered': len(data)
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'data': [],
                'recordsTotal': 0,
                'recordsFiltered': 0
            })


class EditarModuloView(LoginRequiredMixin, UpdateView):
    model = Modulo
    form_class = ModuloForm
    template_name = 'app_user/modulo_editar.html'
    success_url = reverse_lazy('app_usuario:listar_modulo')

    def form_valid(self, form):
        messages.success(self.request, f'Módulo "{form.instance.nombre}" actualizado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class EliminarModuloView(LoginRequiredMixin, DeleteView):
    model = Modulo
    template_name = 'app_user/modulo_eliminar.html'
    success_url = reverse_lazy('app_usuario:listar_modulo')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        messages.success(request, f'Módulo "{nombre}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)
