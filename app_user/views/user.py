from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import *
from django.shortcuts import render, redirect
from app_user.forms import GroupForm, CustomUserCreationForm
from app_user.models import GrupoModulo
from app_user.forms import UserForm
from app_user.models import User
from app_user.forms import ModuloForm, TipoModuloForm
from app_user.models import Modulo, TipoModulo
import json


class crearUsuarioView(LoginRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'app_user/user_crear.html'
    success_url = reverse_lazy('app_usuario:listar_usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Ingresar Usuario'
        context['entity'] = 'Usuario'
        context['action'] = 'crear'
        context['all_permissions'] = Permission.objects.all().select_related('content_type').order_by(
            'content_type__app_label', 'codename')
        return context

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

            # Asignar grupos y permisos
            if form.cleaned_data.get('groups'):
                self.object.groups.set(form.cleaned_data['groups'])
            if form.cleaned_data.get('user_permissions'):
                self.object.user_permissions.set(form.cleaned_data['user_permissions'])

            messages.success(self.request, f'Usuario "{self.object.username}" creado exitosamente.')
            return response
        except Exception as e:
            messages.error(self.request, f'Error al crear usuario: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        print("Errores del formulario:", form.errors)  # Para debug
        return super().form_invalid(form)


class actualizarUsuarioView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'app_user/user_crear.html'
    success_url = reverse_lazy('app_usuario:listar_usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Usuario'
        context['entity'] = 'Usuario'
        context['action'] = 'editar'
        context['all_permissions'] = Permission.objects.all().select_related('content_type').order_by(
            'content_type__app_label', 'codename')
        return context

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

            if form.cleaned_data.get('groups'):
                self.object.groups.set(form.cleaned_data['groups'])
            if form.cleaned_data.get('user_permissions'):
                self.object.user_permissions.set(form.cleaned_data['user_permissions'])

            messages.success(self.request, f'Usuario "{self.object.username}" actualizado exitosamente.')
            return response
        except Exception as e:
            messages.error(self.request, f'Error al actualizar usuario: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        print("Errores del formulario:", form.errors)  # Para debug
        return super().form_invalid(form)


class eliminarUsuarioView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'app_user/user_eliminar.html'
    success_url = reverse_lazy('app_usuario:listar_usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Eliminar Usuario'
        context['entity'] = 'Usuario'
        context['action'] = 'eliminar'
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.username
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f'Usuario "{nombre}" eliminado exitosamente.')
            return response
        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')
            return redirect(self.success_url)


class listarUsuarioView(LoginRequiredMixin, ListView):
    model = User
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Usuario'
        return context


class detalleUsuarioView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'app_user/user_detail.html'
    context_object_name = 'usuario'


class listarGrupoView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'app_user/group_listar.html'
    context_object_name = 'grupos'

    def group_to_json(self, group):
        """Método para convertir grupo a JSON"""
        modulos_grupo = GrupoModulo.objects.filter(grupo=group).select_related('modulo')
        modulos = [gm.modulo.nombre for gm in modulos_grupo]

        return {
            'id': group.id,
            'name': group.name,
            'users_count': group.user_set.count(),
            'permissions_count': group.permissions.count(),
            'modulos': modulos,
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
                for group in Group.objects.all():
                    data.append(self.group_to_json(group))
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Grupos'
        return context


class listarGrupoAjaxView(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return self.handle_request(request)

    def post(self, request):
        return self.handle_request(request)

    def handle_request(self, request):
        try:
            grupos = Group.objects.all().order_by('name')

            data = []
            for grupo in grupos:
                modulos_grupo = GrupoModulo.objects.filter(grupo=grupo).select_related('modulo')
                modulos = [gm.modulo.nombre for gm in modulos_grupo]

                data.append({
                    'id': grupo.id,
                    'name': grupo.name,
                    'users_count': grupo.user_set.count(),
                    'permissions_count': grupo.permissions.count(),
                    'modulos': modulos,
                    'acciones': f'''
                        <div class="btn-group" role="group">
                            <a href="{reverse_lazy('app_usuario:actualizar_grupo', kwargs={'pk': grupo.id})}" class="btn btn-sm btn-warning" title="Editar">
                                <i class="fas fa-edit"></i>
                            </a>
                            <button class="btn btn-sm btn-danger" onclick="eliminarGrupo({grupo.id})" title="Eliminar">
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


class crearGrupoView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'app_user/group_crear.html'
    success_url = reverse_lazy('app_usuario:listar_grupo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Crear Grupo'
        context['modulos'] = Modulo.objects.select_related('tipo').all().order_by('tipo__nombre', 'nombre')
        context['all_permissions'] = Permission.objects.all().select_related('content_type').order_by(
            'content_type__app_label', 'codename')
        return context

    def form_valid(self, form):
        try:
            # Primero guardamos el grupo
            response = super().form_valid(form)

            # Asignar permisos
            if form.cleaned_data.get('permissions'):
                self.object.permissions.set(form.cleaned_data['permissions'])

            # Asignar módulos
            selected_modules = self.request.POST.get('selected_modules', '[]')
            print(f"Módulos seleccionados (raw): {selected_modules}")  # Debug

            try:
                if selected_modules and selected_modules != '[]':
                    module_ids = json.loads(selected_modules)
                    print(f"Módulos parseados: {module_ids}")  # Debug

                    # Eliminar asignaciones anteriores
                    GrupoModulo.objects.filter(grupo=self.object).delete()

                    # Crear nuevas asignaciones
                    created_count = 0
                    for module_id in module_ids:
                        try:
                            modulo = Modulo.objects.get(id=module_id)
                            GrupoModulo.objects.create(grupo=self.object, modulo=modulo)
                            created_count += 1
                            print(f"Módulo asignado: {modulo.nombre}")  # Debug
                        except Modulo.DoesNotExist:
                            print(f"Módulo con ID {module_id} no existe")  # Debug
                            continue

                    messages.success(self.request,
                                     f'Grupo "{self.object.name}" creado exitosamente con {created_count} módulos asignados.')
                else:
                    messages.success(self.request,
                                     f'Grupo "{self.object.name}" creado exitosamente sin módulos asignados.')

            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error al procesar módulos: {str(e)}")  # Debug
                messages.warning(self.request,
                                 f'Grupo "{self.object.name}" creado, pero hubo un error al asignar módulos: {str(e)}')

            return response

        except Exception as e:
            print(f"Error general en form_valid: {str(e)}")  # Debug
            messages.error(self.request, f'Error al crear grupo: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        print(f"Errores del formulario: {form.errors}")  # Debug
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class actualizarGrupoView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'app_user/group_crear.html'
    success_url = reverse_lazy('app_usuario:listar_grupo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Actualizar Grupo'
        context['modulos'] = Modulo.objects.select_related('tipo').all().order_by('tipo__nombre', 'nombre')
        context['all_permissions'] = Permission.objects.all().select_related('content_type').order_by(
            'content_type__app_label', 'codename')

        # Obtener módulos ya asignados al grupo
        modulos_asignados = GrupoModulo.objects.filter(grupo=self.object).values_list('modulo_id', flat=True)
        context['modulos_asignados'] = list(modulos_asignados)

        return context

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

            # Asignar permisos
            if form.cleaned_data.get('permissions'):
                self.object.permissions.set(form.cleaned_data['permissions'])

            # Asignar módulos
            selected_modules = self.request.POST.get('selected_modules', '[]')
            print(f"Módulos seleccionados para actualizar: {selected_modules}")  # Debug

            try:
                if selected_modules and selected_modules != '[]':
                    module_ids = json.loads(selected_modules)

                    # Eliminar asignaciones anteriores
                    GrupoModulo.objects.filter(grupo=self.object).delete()

                    # Crear nuevas asignaciones
                    created_count = 0
                    for module_id in module_ids:
                        try:
                            modulo = Modulo.objects.get(id=module_id)
                            GrupoModulo.objects.create(grupo=self.object, modulo=modulo)
                            created_count += 1
                        except Modulo.DoesNotExist:
                            continue

                    messages.success(self.request,
                                     f'Grupo "{self.object.name}" actualizado exitosamente con {created_count} módulos asignados.')
                else:
                    # Si no hay módulos seleccionados, eliminar todas las asignaciones
                    GrupoModulo.objects.filter(grupo=self.object).delete()
                    messages.success(self.request,
                                     f'Grupo "{self.object.name}" actualizado exitosamente sin módulos asignados.')

            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error al procesar módulos: {str(e)}")  # Debug
                messages.warning(self.request,
                                 f'Grupo "{self.object.name}" actualizado, pero hubo un error al asignar módulos: {str(e)}')

            return response

        except Exception as e:
            print(f"Error general en form_valid: {str(e)}")  # Debug
            messages.error(self.request, f'Error al actualizar grupo: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        print(f"Errores del formulario: {form.errors}")  # Debug
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class eliminarGrupoView(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = 'app_user/group_eliminar.html'
    success_url = reverse_lazy('app_usuario:listar_grupo')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.name

        try:
            # Eliminar relaciones con módulos
            GrupoModulo.objects.filter(grupo=self.object).delete()

            response = super().delete(request, *args, **kwargs)
            messages.success(request, f'Grupo "{nombre}" eliminado exitosamente.')
            return response
        except Exception as e:
            messages.error(request, f'Error al eliminar grupo: {str(e)}')
            return redirect(self.success_url)


class detalleGrupoView(LoginRequiredMixin, DetailView):
    model = Group
    template_name = 'app_user/group_detail.html'
    context_object_name = 'grupo'


class detalleModuloView(LoginRequiredMixin, DetailView):
    model = Modulo
    template_name = 'app_user/modulo_detail.html'
    context_object_name = 'modulo'


class CrearTipoModuloView(LoginRequiredMixin, CreateView):
    model = TipoModulo
    form_class = TipoModuloForm
    template_name = 'app_user/tipo_modulo_crear.html'
    success_url = reverse_lazy('app_usuario:listar_tipo_modulo')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, f'Tipo de módulo "{form.instance.nombre}" creado exitosamente.')
            return response
        except Exception as e:
            messages.error(self.request, f'Error al crear tipo de módulo: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        print(f"Errores del formulario: {form.errors}")  # Debug
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
        try:
            response = super().form_valid(form)
            messages.success(self.request, f'Tipo de módulo "{form.instance.nombre}" actualizado exitosamente.')
            return response
        except Exception as e:
            messages.error(self.request, f'Error al actualizar tipo de módulo: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        print(f"Errores del formulario: {form.errors}")  # Debug
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class EliminarTipoModuloView(LoginRequiredMixin, DeleteView):
    model = TipoModulo
    template_name = 'app_user/tipo_modulo_eliminar.html'
    success_url = reverse_lazy('app_usuario:listar_tipo_modulo')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f'Tipo de módulo "{nombre}" eliminado exitosamente.')
            return response
        except Exception as e:
            messages.error(request, f'Error al eliminar tipo de módulo: {str(e)}')
            return redirect(self.success_url)


class CrearModuloView(LoginRequiredMixin, CreateView):
    model = Modulo
    form_class = ModuloForm
    template_name = 'app_user/modulo_crear.html'
    success_url = reverse_lazy('app_usuario:listar_modulo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_modulo'] = TipoModulo.objects.all().order_by('nombre')
        return context

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, f'Módulo "{form.instance.nombre}" creado exitosamente.')
            return response
        except Exception as e:
            messages.error(self.request, f'Error al crear módulo: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        print(f"Errores del formulario: {form.errors}")  # Debug
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class ListarModuloView(LoginRequiredMixin, ListView):
    model = Modulo
    template_name = 'app_user/modulo_listar.html'
    context_object_name = 'modulos'

    def modulo_to_json(self, modulo):
        """Método para convertir módulo a JSON"""
        return {
            'id': modulo.id,
            'nombre': modulo.nombre,
            'tipo': modulo.tipo.nombre if modulo.tipo else 'Sin tipo',
            'url': modulo.url or '',
            'icono': modulo.icono or 'fas fa-cube',
            'orden': getattr(modulo, 'orden', 0),
            'activo': getattr(modulo, 'activo', True),
            'fecha_creacion': modulo.fecha_creacion.strftime('%d/%m/%Y %H:%M') if hasattr(modulo,
                                                                                          'fecha_creacion') else '',
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
                for modulo in Modulo.objects.select_related('tipo').all():
                    data.append(self.modulo_to_json(modulo))
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'Módulos'
        return context


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
                    'icono': modulo.icono or 'fas fa-cube',
                    'orden': getattr(modulo, 'orden', 0),
                    'activo': getattr(modulo, 'activo', True),
                    'fecha_creacion': modulo.fecha_creacion.strftime('%d/%m/%Y %H:%M') if hasattr(modulo,
                                                                                                  'fecha_creacion') else '',
                    'acciones': f'''
                        <div class="btn-group" role="group">
                            <a href="{reverse_lazy('app_usuario:actualizar_modulo', kwargs={'pk': modulo.id})}" class="btn btn-sm btn-warning" title="Editar">
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
        try:
            response = super().form_valid(form)
            print('llego a response')
            return response
        except Exception as e:
            return self.form_invalid(form)

    def form_invalid(self, form):
        print(f"Errores del formulario: {form.errors}")  # Debug
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class EliminarModuloView(LoginRequiredMixin, DeleteView):
    model = Modulo
    template_name = 'app_user/modulo_eliminar.html'
    success_url = reverse_lazy('app_usuario:listar_modulo')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f'Módulo "{nombre}" eliminado exitosamente.')
            return response
        except Exception as e:
            messages.error(request, f'Error al eliminar módulo: {str(e)}')
            return redirect(self.success_url)
