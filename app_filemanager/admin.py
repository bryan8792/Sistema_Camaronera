from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import File, Folder, SharedLink, FolderPermission, FilePermission


@admin.register(File)
class FileAdmin(GuardedModelAdmin):
    list_display = ['name', 'owner', 'folder', 'file_type', 'get_file_size_display', 'download_count', 'is_public',
                    'created_at']
    list_filter = ['file_type', 'is_public', 'created_at', 'owner']
    search_fields = ['name', 'owner__username', 'description']
    readonly_fields = ['size', 'file_type', 'mime_type', 'download_count', 'created_at', 'updated_at']
    raw_id_fields = ['owner', 'folder']

    def get_file_size_display(self, obj):
        return obj.get_file_size_display()

    get_file_size_display.short_description = 'Tamaño'


@admin.register(Folder)
class FolderAdmin(GuardedModelAdmin):
    list_display = ['name', 'owner', 'parent', 'get_file_count', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at', 'owner']
    search_fields = ['name', 'owner__username', 'description']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['owner', 'parent']

    def get_file_count(self, obj):
        return obj.get_file_count()

    get_file_count.short_description = 'Archivos'


@admin.register(FolderPermission)
class FolderPermissionAdmin(admin.ModelAdmin):
    list_display = ['folder', 'user', 'permission_level', 'granted_by', 'created_at']
    list_filter = ['permission_level', 'created_at']
    search_fields = ['folder__name', 'user__username', 'granted_by__username']
    raw_id_fields = ['folder', 'user', 'granted_by']


@admin.register(FilePermission)
class FilePermissionAdmin(admin.ModelAdmin):
    list_display = ['file', 'user', 'permission_level', 'granted_by', 'created_at']
    list_filter = ['permission_level', 'created_at']
    search_fields = ['file__name', 'user__username', 'granted_by__username']
    raw_id_fields = ['file', 'user', 'granted_by']


@admin.register(SharedLink)
class SharedLinkAdmin(admin.ModelAdmin):
    list_display = ['get_item_name', 'shared_by', 'shared_with', 'permission_level', 'is_public', 'expires_at',
                    'created_at']
    list_filter = ['permission_level', 'is_public', 'created_at']
    search_fields = ['shared_by__username', 'shared_with__username', 'token']
    readonly_fields = ['token', 'created_at']
    raw_id_fields = ['shared_by', 'shared_with', 'folder', 'file']

    def get_item_name(self, obj):
        item = obj.get_item()
        return item.name if item else 'N/A'

    get_item_name.short_description = 'Item'
