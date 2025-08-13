from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import Http404, JsonResponse, FileResponse, HttpResponseForbidden, HttpResponseNotAllowed, \
    HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from guardian.shortcuts import get_objects_for_user, assign_perm, remove_perm, get_users_with_perms
from app_filemanager.models import File, Folder, SharedLink, FolderPermission, FilePermission
from app_filemanager.forms import (
    FileUploadForm, MultipleFileUploadForm, FolderCreateForm,
    FolderEditForm, FileEditForm, FolderPermissionForm, FilePermissionForm
)
from app_user.models import User
from app_user.forms import UserForm
from django.db.models import Q
from ..models import Folder, FolderPermission  # ajusta import a tu estructura


LEVEL_NUM = {"read": 1, "write": 2, "admin": 3}

def _user_level_on_folder(user, folder):
  if not user.is_authenticated:
    return 0
  if folder is None:
    return 3  # opcional: trata raíz como libre si es dueño del file; ajusta a tu política
  if folder.owner_id == user.id:
    return 3
  perm = FolderPermission.objects.filter(folder=folder, user=user).values_list("permission_level", flat=True).first()
  return LEVEL_NUM.get(perm, 0) if perm else 0

@require_POST
@login_required
@csrf_exempt
def ajax_file_upload(request):
  uploaded_file = request.FILES.get('file')
  if not uploaded_file:
    return HttpResponseBadRequest("Falta archivo")
  folder_id = request.POST.get('folder')
  dest = get_object_or_404(Folder, pk=folder_id) if folder_id else None

  if dest and _user_level_on_folder(request.user, dest) < LEVEL_NUM["write"]:
    return HttpResponseForbidden("Sin permiso de escritura")

  try:
    File.objects.create(owner=request.user, name=uploaded_file.name, file=uploaded_file, folder=dest)
    return JsonResponse({"ok": True})
  except Exception as e:
    return JsonResponse({"ok": False, "error": str(e)}, status=500)


def _can_manage_folder(user, folder: Folder) -> bool:
    if not user.is_authenticated:
        return False
    return folder.owner_id == user.id or FolderPermission.objects.filter(folder=folder, user=user, permission_level="admin").exists()

@login_required
def folder_permission_update(request, folder_id: int, perm_id: int):
    folder = get_object_or_404(Folder, pk=folder_id)
    if not _can_manage_folder(request.user, folder):
        return HttpResponseForbidden("No autorizado")
    if request.method != "POST":
        return HttpResponseBadRequest("Método inválido")
    level = (request.POST.get("permission_level") or "").strip()
    if level not in {"read", "write", "admin"}:
        messages.error(request, "Nivel inválido.")
        return redirect("app_filemanager:folder_permissions", folder_id=folder.id)

    perm = get_object_or_404(FolderPermission, pk=perm_id, folder=folder)
    perm.permission_level = level
    perm.granted_by = request.user
    perm.save()

    # Si usas guardian, sincroniza aquí (opcional)
    messages.success(request, f"Permiso actualizado a '{level}'.")
    return redirect("app_filemanager:folder_permissions", folder_id=folder.id)

@login_required
def folder_permission_delete(request, folder_id: int, perm_id: int):
    folder = get_object_or_404(Folder, pk=folder_id)
    if not _can_manage_folder(request.user, folder):
        return HttpResponseForbidden("No autorizado")
    if request.method != "POST":
        return HttpResponseBadRequest("Método inválido")
    perm = get_object_or_404(FolderPermission, pk=perm_id, folder=folder)
    perm.delete()
    messages.success(request, "Permiso revocado.")
    return redirect("app_filemanager:folder_permissions", folder_id=folder.id)

def _is_descendant(candidate: Folder | None, ancestor: Folder) -> bool:
    """
    True si 'candidate' está dentro del subárbol de 'ancestor'.
    Sube por la cadena de padres desde candidate hasta None.
    """
    cur = candidate
    while cur is not None:
        if cur.id == ancestor.id:
            return True
        cur = cur.parent
    return False

@require_POST
@login_required
def ajax_move(request):
    """
    Mueve un archivo o carpeta a una carpeta destino.
    Espera POST form-data con:
      - type: 'file' | 'folder'
      - id:   id del file/folder a mover
      - target: id de carpeta destino (vacío o omitido => mover a raíz)
    Retorna JSON: { ok: true } o { ok: false, error: "..." }
    """
    item_type = (request.POST.get("type") or "").strip()
    item_id = request.POST.get("id")
    target_id = request.POST.get("target")  # puede venir None o vacío => raíz

    if item_type not in {"file", "folder"}:
        return HttpResponseBadRequest("Tipo inválido")

    # Destino
    target_folder = None
    if target_id:
        target_folder = get_object_or_404(Folder, pk=target_id)

    try:
        if item_type == "file":
            item = get_object_or_404(File, pk=item_id)
            source_folder = item.folder  # puede ser None (raíz)

            # Permisos: mover requiere admin en origen (o owner) y write/admin en destino (si hay destino)
            src_level = _user_level_on_folder(request.user, source_folder) if source_folder else 3  # raíz: tratamos como dueño del propio file
            dst_level = _user_level_on_folder(request.user, target_folder) if target_folder else 3  # mover a raíz: permitir al dueño/admin

            # Si no es owner del file, revisa nivel en origen
            is_owner = (item.owner_id == request.user.id)
            if not is_owner and src_level < LEVEL_NUM["admin"]:
                return HttpResponseForbidden("Sin permisos (origen)")

            if target_folder and dst_level < LEVEL_NUM["write"]:
                return HttpResponseForbidden("Sin permisos (destino)")

            item.folder = target_folder
            item.save(update_fields=["folder"])
            return JsonResponse({"ok": True})
        else:
            folder = get_object_or_404(Folder, pk=item_id)
            source_parent = folder.parent  # puede ser None
            # Evitar mover dentro de sí o un descendiente
            if target_folder and (target_folder.id == folder.id or _is_descendant(target_folder, folder)):
                return JsonResponse({"ok": False, "error": "No puedes mover una carpeta dentro de sí misma o de un descendiente."}, status=400)

            src_level = _user_level_on_folder(request.user, source_parent) if source_parent else 3
            dst_level = _user_level_on_folder(request.user, target_folder) if target_folder else 3

            is_owner = (folder.owner_id == request.user.id)
            if not is_owner and src_level < LEVEL_NUM["admin"]:
                return HttpResponseForbidden("Sin permisos (origen)")

            if target_folder and dst_level < LEVEL_NUM["write"]:
                return HttpResponseForbidden("Sin permisos (destino)")

            folder.parent = target_folder
            folder.save(update_fields=["parent"])
            return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)

User = get_user_model()

def user_search(request):
    """
    Devuelve JSON con usuarios activos para autocompletar.
    Params:
      - q: texto a buscar (username, names, email)
      - folder: id opcional de carpeta para excluir ya asignados
    """
    if not request.user.is_authenticated:
        return JsonResponse({"results": []})

    q = (request.GET.get("q") or "").strip()
    folder_id = request.GET.get("folder")
    users = User.objects.filter(is_active=True)

    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(names__icontains=q) |
            Q(email__icontains=q)
        )

    # Excluir el propio usuario
    users = users.exclude(id=request.user.id)

    # Si llega folder, excluir usuarios que ya tengan un registro de permiso para esa carpeta
    if folder_id:
        assigned_ids = FolderPermission.objects.filter(folder_id=folder_id).values_list("user_id", flat=True)
        users = users.exclude(id__in=assigned_ids)

    users = users.order_by("names", "username")[:20]

    results = [
        {
            "id": u.id,
            "username": u.username,
            "full_name": (u.get_full_name() or u.username),
            "email": u.email,
        }
        for u in users
    ]
    return JsonResponse({"results": results})


def _can_manage_folder(user, folder: Folder) -> bool:
    """Dueño o quien tenga nivel admin en FolderPermission."""
    if not user.is_authenticated:
        return False
    if folder.owner_id == user.id:
        return True
    return FolderPermission.objects.filter(folder=folder, user=user, permission_level="admin").exists()


def folder_permissions(request, folder_id: int):
    """Renderiza la pantalla de permisos (lista actual + formulario)."""
    folder = get_object_or_404(Folder, pk=folder_id)
    if not _can_manage_folder(request.user, folder):
        return HttpResponseForbidden("No autorizado")

    permissions = FolderPermission.objects.filter(folder=folder).select_related("user", "granted_by").order_by("user__names", "user__username")

    context = {
        "folder": folder,
        "permissions": permissions,
    }
    return render(request, "app_filemanager/filemanager/folder_permissions.html", context)


def folder_permission_create(request, folder_id: int):
    """
    Crea o actualiza el permiso de un usuario sobre la carpeta.
    Espera POST con:
      - username
      - permission_level: 'read' | 'write' | 'admin'
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    folder = get_object_or_404(Folder, pk=folder_id)
    if not _can_manage_folder(request.user, folder):
        return HttpResponseForbidden("No autorizado")

    username = (request.POST.get("username") or "").strip()
    level = (request.POST.get("permission_level") or "").strip()

    if not username or level not in {"read", "write", "admin"}:
        messages.error(request, "Datos incompletos o inválidos.")
        return redirect("app_filemanager:folder_permissions", folder_id=folder.id)

    try:
        target_user = User.objects.get(username=username, is_active=True)
    except User.DoesNotExist:
        messages.error(request, f"Usuario '{username}' no encontrado o inactivo.")
        return redirect("app_filemanager:folder_permissions", folder_id=folder.id)

    perm, created = FolderPermission.objects.get_or_create(
        folder=folder,
        user=target_user,
        defaults={"permission_level": level, "granted_by": request.user},
    )
    if not created:
        perm.permission_level = level
        perm.granted_by = request.user
        perm.save()

    # Si usas django-guardian, aquí podrías sincronizar permisos de objeto:
    # from guardian.shortcuts import assign_perm, remove_perm
    # def sync_guardian(level: str):
    #     # ejemplo de mapeo, ajusta a tus codenames reales
    #     all_perms = ["view_folder", "change_folder", "delete_folder", "add_file", "change_file", "delete_file"]
    #     for p in all_perms:
    #         remove_perm(p, target_user, folder)
    #     if level in {"read", "write", "admin"}:
    #         assign_perm("view_folder", target_user, folder)
    #     if level in {"write", "admin"}:
    #         for p in ["change_folder", "add_file", "change_file", "delete_file"]:
    #             assign_perm(p, target_user, folder)
    #     if level == "admin":
    #         assign_perm("delete_folder", target_user, folder)
    # sync_guardian(level)

    messages.success(request, f"Permisos de {target_user.username} actualizados a '{level}'.")
    return redirect("app_filemanager:folder_permissions", folder_id=folder.id)


class DashboardView(LoginRequiredMixin, View):
    """Dashboard with statistics and recent files"""

    def get(self, request):
        # Get user statistics
        total_files = File.objects.filter(owner=request.user).count()
        total_folders = Folder.objects.filter(owner=request.user).count()
        total_size = File.objects.filter(owner=request.user).aggregate(
            total=Sum('size'))['total'] or 0

        # Recent files
        recent_files = File.objects.filter(owner=request.user)[:10]

        # Recent folders
        recent_folders = Folder.objects.filter(owner=request.user)[:5]

        # Shared items
        shared_with_me = SharedLink.objects.filter(shared_with=request.user)[:5]

        # File type distribution
        file_types = File.objects.filter(owner=request.user).values('file_type').annotate(
            count=Count('id')).order_by('-count')[:10]

        context = {
            'total_files': total_files,
            'total_folders': total_folders,
            'total_size': self.format_size(total_size),
            'recent_files': recent_files,
            'recent_folders': recent_folders,
            'shared_with_me': shared_with_me,
            'file_types': file_types,
        }

        return render(request, 'app_filemanager/filemanager/dashboard.html', context)

    def format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"


class FileListView(LoginRequiredMixin, ListView):
    """List files and folders with advanced filtering"""
    model = File
    template_name = 'app_filemanager/filemanager/file_list.html'
    context_object_name = 'files'
    paginate_by = 20

    def get_queryset(self):
        folder_id = self.kwargs.get('folder_id')
        current_folder = None

        if folder_id:
            current_folder = get_object_or_404(Folder, id=folder_id)
            # Check permissions
            if not (current_folder.owner == self.request.user or
                    current_folder.is_public or
                    self.request.user.has_perm('app_filemanager.view_folder', current_folder)):
                raise Http404("No tienes permiso para ver esta carpeta")

        # Get files in current directory
        files = get_objects_for_user(
            self.request.user,
            'app_filemanager.view_file',
            klass=File
        ).filter(folder=current_folder)

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            files = files.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(file_type__icontains=search_query)
            )

        # Filter by file type
        file_type = self.request.GET.get('type')
        if file_type:
            files = files.filter(file_type__icontains=file_type)

        # Sort options
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['name', '-name', 'size', '-size', 'created_at', '-created_at']:
            files = files.order_by(sort_by)

        return files

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder_id = self.kwargs.get('folder_id')
        current_folder = None

        if folder_id:
            current_folder = get_object_or_404(Folder, id=folder_id)

        # Get folders in current directory
        folders = get_objects_for_user(
            self.request.user,
            'app_filemanager.view_folder',
            klass=Folder
        ).filter(parent=current_folder)

        # Search in folders too
        search_query = self.request.GET.get('search')
        if search_query:
            folders = folders.filter(name__icontains=search_query)

        # Breadcrumb navigation
        breadcrumbs = []
        if current_folder:
            breadcrumbs = current_folder.get_breadcrumbs()

        context.update({
            'folders': folders,
            'current_folder': current_folder,
            'breadcrumbs': breadcrumbs,
            'search_query': search_query,
            'upload_form': FileUploadForm(),
            'folder_form': FolderCreateForm(),
            'can_upload': True,
            'can_create_folder': True,
        })

        return context


class FileUploadView(LoginRequiredMixin, View):
    """Upload files with advanced features"""
    template_name = 'app_filemanager/filemanager/file_upload.html'

    def get(self, request):
        # Get user folders for dropdown
        user_folders = Folder.objects.filter(owner=request.user).order_by('name')

        # Get recent files
        recent_files = File.objects.filter(owner=request.user)[:10]

        # Create form with user context
        form = MultipleFileUploadForm(user=request.user)

        context = {
            'user_folders': user_folders,
            'recent_files': recent_files,
            'form': form,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        # Handle multiple file upload
        uploaded_files = request.FILES.getlist('files')
        folder_id = request.POST.get('folder_id')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'on'

        if not uploaded_files:
            messages.error(request, 'No se seleccionaron archivos.')
            return redirect('app_filemanager:file_upload')

        # Get folder if specified
        folder = None
        if folder_id:
            try:
                folder = Folder.objects.get(id=folder_id, owner=request.user)
            except Folder.DoesNotExist:
                messages.error(request, 'Carpeta no encontrada.')
                return redirect('app_filemanager:file_upload')

        # Process each file
        uploaded_count = 0
        errors = []

        for uploaded_file in uploaded_files:
            try:
                # Create file instance
                file_obj = File(
                    name=uploaded_file.name,
                    file=uploaded_file,
                    folder=folder,
                    owner=request.user,
                    description=description,
                    is_public=is_public
                )
                file_obj.save()
                uploaded_count += 1

            except Exception as e:
                errors.append(f'Error con {uploaded_file.name}: {str(e)}')

        # Show results
        if uploaded_count > 0:
            messages.success(
                request,
                f'{uploaded_count} archivo(s) subido(s) exitosamente!'
            )

        if errors:
            for error in errors:
                messages.error(request, error)

        # Redirect based on folder
        if folder:
            return redirect('app_filemanager:folder_detail', pk=folder.pk)
        else:
            return redirect('app_filemanager:file_list')


class SingleFileUploadView(LoginRequiredMixin, CreateView):
    """Single file upload view"""
    model = File
    form_class = FileUploadForm
    template_name = 'app_filemanager/filemanager/single_file_upload.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.name = self.request.FILES['file'].name

        # Set folder if specified
        folder_id = self.request.POST.get('folder_id')
        if folder_id:
            folder = get_object_or_404(Folder, id=folder_id)
            # Check permissions
            if not (folder.owner == self.request.user or
                    self.request.user.has_perm('app_filemanager.edit_folder', folder)):
                messages.error(self.request, "No tienes permiso para subir archivos a esta carpeta.")
                return redirect('app_filemanager:file_list')
            form.instance.folder = folder

        response = super().form_valid(form)
        messages.success(self.request, f'Archivo "{self.object.name}" subido exitosamente!')

        if folder_id:
            return redirect('app_filemanager:folder_detail', pk=folder_id)
        return redirect('app_filemanager:file_list')

    def get_success_url(self):
        return reverse('app_filemanager:file_list')


class FolderCreateView(LoginRequiredMixin, CreateView):
    """Create new folders"""
    model = Folder
    form_class = FolderCreateForm
    template_name = 'app_filemanager/filemanager/folder_create.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user

        # Set parent folder if specified
        parent_id = self.request.POST.get('parent_id')
        if parent_id:
            parent_folder = get_object_or_404(Folder, id=parent_id)
            # Check permissions
            if not (parent_folder.owner == self.request.user or
                    self.request.user.has_perm('app_filemanager.edit_folder', parent_folder)):
                messages.error(self.request, "No tienes permiso para crear carpetas aquí.")
                return redirect('app_filemanager:file_list')
            form.instance.parent = parent_folder

        try:
            response = super().form_valid(form)
            messages.success(self.request, f'Carpeta "{self.object.name}" creada exitosamente!')
            return response
        except Exception as e:
            messages.error(self.request, 'Ya existe una carpeta con este nombre en esta ubicación.')
            return self.form_invalid(form)

    def get_success_url(self):
        if self.object.parent:
            return reverse('app_filemanager:folder_detail', kwargs={'pk': self.object.parent.pk})
        return reverse('app_filemanager:file_list')


class FolderDetailView(DetailView):
    """Folder detail view with contents"""
    model = Folder
    template_name = 'app_filemanager/filemanager/folder_detail.html'
    context_object_name = 'folder'

    def get_object(self):
        folder = super().get_object()
        # Check permissions
        if not (folder.owner == self.request.user or
                folder.is_public or
                self.request.user.has_perm('app_filemanager.view_folder', folder)):
            raise Http404("No tienes permiso para ver esta carpeta")
        return folder

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder = self.object
        context["can_upload"] = _user_level_on_folder(self.request.user, folder) >= LEVEL_NUM["write"]
        if "folders" not in context:
            context["folders"] = Folder.objects.filter(parent=folder)
        if "files" not in context:
            context["files"] = folder.files.all()
            # breadcrumbs si no lo tienes
        if "breadcrumbs" not in context:
            crumbs = []
            cur = folder
            while cur and cur.parent:
                crumbs.insert(0, {"pk": cur.parent.id, "name": cur.parent.name})
                cur = cur.parent
            context["breadcrumbs"] = crumbs
        # Get subfolders
        subfolders = get_objects_for_user(
            self.request.user,
            'app_filemanager.view_folder',
            klass=Folder
        ).filter(parent=folder)

        # Get files
        files = get_objects_for_user(
            self.request.user,
            'app_filemanager.view_file',
            klass=File
        ).filter(folder=folder)

        paginator = Paginator(files, 20)
        page_number = self.request.GET.get('page')
        files_page = paginator.get_page(page_number)

        context.update({
            'subfolders': subfolders,
            'files': files_page,
            'breadcrumbs': folder.get_breadcrumbs(),
            'can_edit': (folder.owner == self.request.user or
                         self.request.user.has_perm('app_filemanager.edit_folder', folder)),
            'can_delete': (folder.owner == self.request.user or
                           self.request.user.has_perm('app_filemanager.delete_folder', folder)),
            'can_share': (folder.owner == self.request.user or
                          self.request.user.has_perm('app_filemanager.share_folder', folder)),
        })

        return context


class FileDownloadView(LoginRequiredMixin, View):
    """Download files with permission check"""

    def get(self, request, pk):
        file_obj = get_object_or_404(File, pk=pk)

        # Check permissions
        if not (file_obj.owner == request.user or
                file_obj.is_public or
                request.user.has_perm('app_filemanager.download_file', file_obj)):
            raise Http404("No tienes permiso para descargar este archivo")

        try:
            # Increment download count
            file_obj.download_count += 1
            file_obj.save(update_fields=['download_count'])

            response = FileResponse(
                file_obj.file.open('rb'),
                as_attachment=True,
                filename=file_obj.name
            )
            return response
        except FileNotFoundError:
            messages.error(request, 'Archivo no encontrado en el servidor.')
            return redirect('app_filemanager:file_list')


class FileDeleteView(LoginRequiredMixin, DeleteView):
    """Delete files with permission check"""
    model = File
    template_name = 'app_filemanager/filemanager/file_confirm_delete.html'

    def get_object(self):
        file_obj = super().get_object()
        # Check permissions
        if not (file_obj.owner == self.request.user or
                self.request.user.has_perm('app_filemanager.delete_file', file_obj)):
            raise Http404("No tienes permiso para eliminar este archivo")
        return file_obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        folder_id = self.object.folder.pk if self.object.folder else None

        try:
            # Delete physical file
            if self.object.file:
                self.object.file.delete()

            messages.success(request, f'Archivo "{self.object.name}" eliminado exitosamente!')
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, 'Error al eliminar el archivo.')
            return redirect('app_filemanager:file_list')

    def get_success_url(self):
        if hasattr(self, 'object') and self.object.folder:
            return reverse('app_filemanager:folder_detail', kwargs={'pk': self.object.folder.pk})
        return reverse('app_filemanager:file_list')


class FolderDeleteView(LoginRequiredMixin, DeleteView):
    """Delete folders with permission check"""
    model = Folder
    template_name = 'app_filemanager/filemanager/folder_confirm_delete.html'

    def get_object(self):
        folder = super().get_object()
        # Check permissions
        if not (folder.owner == self.request.user or
                self.request.user.has_perm('app_filemanager.delete_folder', folder)):
            raise Http404("No tienes permiso para eliminar esta carpeta")
        return folder

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        parent_id = self.object.parent.pk if self.object.parent else None

        try:
            # Delete all files in folder
            files_in_folder = File.objects.filter(folder=self.object)
            for file_obj in files_in_folder:
                if file_obj.file:
                    file_obj.file.delete()

            messages.success(request, f'Carpeta "{self.object.name}" eliminada exitosamente!')
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, 'Error al eliminar la carpeta.')
            return redirect('app_filemanager:file_list')

    def get_success_url(self):
        if hasattr(self, 'object') and self.object.parent:
            return reverse('app_filemanager:folder_detail', kwargs={'pk': self.object.parent.pk})
        return reverse('app_filemanager:file_list')



@method_decorator(csrf_exempt, name='dispatch')
class AjaxFileUploadView(View):
    def post(self, request, *args, **kwargs):
        # Usamos el formulario pasando user como keyword argument
        form = MultipleFileUploadForm(request.POST, request.FILES, user=request.user)

        # Obtén los archivos enviados por JS
        files = request.FILES.getlist('files')

        if form.is_valid():
            folder = form.cleaned_data.get('folder', None)
            description = form.cleaned_data.get('description', '')
            is_public = form.cleaned_data.get('is_public', False)

            # Validar permisos de escritura si es carpeta específica
            if folder and _user_level_on_folder(request.user, folder) < LEVEL_NUM["write"]:
                return JsonResponse({'success': False, 'message': 'No tienes permiso de escritura en esta carpeta.'}, status=403)

            uploaded_files = []
            for f in files:
                try:
                    file_instance = File(
                        name=f.name,
                        file=f,
                        description=description,
                        is_public=is_public,
                        owner=request.user,
                        folder=folder
                    )
                    file_instance.save()
                    uploaded_files.append(file_instance.name)
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error al subir {f.name}: {str(e)}'}, status=500)

            return JsonResponse({
                'success': True,
                'message': f'Archivos subidos exitosamente: {", ".join(uploaded_files)}'
            })

        else:
            # Retorna errores de validación del formulario
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# Permission Views
class FolderPermissionListView(LoginRequiredMixin, ListView):
    """List folder permissions"""
    model = FolderPermission
    template_name = 'app_filemanager/filemanager/folder_permissions.html'
    context_object_name = 'permissions'

    def get_queryset(self):
        folder_id = self.kwargs.get('folder_id')
        self.folder = get_object_or_404(Folder, id=folder_id)

        # Check if user is owner or has admin permission
        if not (self.folder.owner == self.request.user or
                self.request.user.has_perm('app_filemanager.share_folder', self.folder)):
            messages.error(self.request, "No tienes permiso para gestionar los permisos de esta carpeta.")
            return FolderPermission.objects.none()

        return FolderPermission.objects.filter(folder=self.folder)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['folder'] = self.folder
        context['form'] = FolderPermissionForm()

        # Get users with Django Guardian permissions
        users_with_perms = get_users_with_perms(self.folder, attach_perms=True)
        context['guardian_permissions'] = users_with_perms

        return context


class FolderPermissionCreateView(LoginRequiredMixin, View):
    """Grant folder permissions to users"""

    def post(self, request, folder_id):
        folder = get_object_or_404(Folder, id=folder_id)

        # Check if user is owner or has admin permission
        if not (folder.owner == request.user or
                request.user.has_perm('app_filemanager.share_folder', folder)):
            messages.error(request, "No tienes permiso para gestionar los permisos de esta carpeta.")
            return redirect('app_filemanager:folder_permissions', folder_id=folder_id)

        form = FolderPermissionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            permission_level = form.cleaned_data['permission_level']

            try:
                user = User.objects.get(username=username)

                # Create or update custom permission
                permission, created = FolderPermission.objects.get_or_create(
                    folder=folder,
                    user=user,
                    defaults={
                        'permission_level': permission_level,
                        'granted_by': request.user
                    }
                )

                if not created:
                    permission.permission_level = permission_level
                    permission.save()

                # Assign Django Guardian permissions based on level
                self.assign_guardian_permissions(user, folder, permission_level)

                action = "otorgado" if created else "actualizado"
                messages.success(request, f'Permiso {action} para {username}')

            except User.DoesNotExist:
                messages.error(request, f'Usuario "{username}" no encontrado.')
        else:
            messages.error(request, 'Datos del formulario inválidos.')

        return redirect('app_filemanager:folder_permissions', folder_id=folder_id)

    def assign_guardian_permissions(self, user, folder, permission_level):
        """Assign Guardian permissions based on permission level"""
        # Remove existing permissions
        remove_perm('app_filemanager.view_folder', user, folder)
        remove_perm('app_filemanager.edit_folder', user, folder)
        remove_perm('app_filemanager.delete_folder', user, folder)
        remove_perm('app_filemanager.share_folder', user, folder)

        # Assign permissions based on level
        if permission_level in ['read', 'write', 'admin']:
            assign_perm('app_filemanager.view_folder', user, folder)

        if permission_level in ['write', 'admin']:
            assign_perm('app_filemanager.edit_folder', user, folder)

        if permission_level == 'admin':
            assign_perm('app_filemanager.delete_folder', user, folder)
            assign_perm('app_filemanager.share_folder', user, folder)


class UserSearchView(LoginRequiredMixin, View):
    """AJAX endpoint for user search"""

    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) >= 2:
            users = User.objects.filter(
                username__icontains=query
            ).exclude(
                id=request.user.id
            )[:10]

            results = [{'username': user.username, 'full_name': user.get_full_name()}
                       for user in users]
            return JsonResponse({'results': results})

        return JsonResponse({'results': []})
