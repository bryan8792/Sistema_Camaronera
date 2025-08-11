from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from guardian.shortcuts import assign_perm
import os

User = get_user_model()


class Folder(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='subfolders', verbose_name="Carpeta Padre")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_folders',
                              verbose_name="Propietario")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_public = models.BooleanField(default=False, verbose_name="Es Público")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        unique_together = ['name', 'parent', 'owner']
        ordering = ['name']
        verbose_name = "Carpeta"
        verbose_name_plural = "Carpetas"
        permissions = [
            ('can_view_folder', 'Can view folder'),
            ('can_edit_folder', 'Can edit folder'),
            ('can_delete_folder', 'Can delete folder'),
            ('can_share_folder', 'Can share folder'),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('filemanager:folder_detail', kwargs={'pk': self.pk})

    def get_path(self):
        """Get the full path of the folder"""
        path = []
        current = self
        while current:
            path.append(current.name)
            current = current.parent
        return '/'.join(reversed(path))

    def get_breadcrumbs(self):
        """Get breadcrumb navigation"""
        breadcrumbs = []
        current = self
        while current:
            breadcrumbs.insert(0, current)
            current = current.parent
        return breadcrumbs

    def get_size(self):
        """Calculate total size of folder including subfolders"""
        total_size = 0
        for file in self.files.all():
            total_size += file.size
        for subfolder in self.subfolders.all():
            total_size += subfolder.get_size()
        return total_size

    def get_file_count(self):
        """Get total number of files in folder and subfolders"""
        count = self.files.count()
        for subfolder in self.subfolders.all():
            count += subfolder.get_file_count()
        return count

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Assign default permissions to owner
        if is_new:
            assign_perm('can_view_folder', self.owner, self)
            assign_perm('can_edit_folder', self.owner, self)
            assign_perm('can_delete_folder', self.owner, self)
            assign_perm('can_share_folder', self.owner, self)


class File(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    file = models.FileField(upload_to='filemanager/uploads/%Y/%m/%d/', verbose_name="Archivo")
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='files', verbose_name="Carpeta")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_files',
                              verbose_name="Propietario")
    size = models.BigIntegerField(default=0, verbose_name="Tamaño")
    file_type = models.CharField(max_length=50, blank=True, verbose_name="Tipo de Archivo")
    mime_type = models.CharField(max_length=100, blank=True, verbose_name="Tipo MIME")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_public = models.BooleanField(default=False, verbose_name="Es Público")
    download_count = models.PositiveIntegerField(default=0, verbose_name="Descargas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Archivo"
        verbose_name_plural = "Archivos"
        permissions = [
            ('can_view_file', 'Can view file'),
            ('can_download_file', 'Can download file'),
            ('can_edit_file', 'Can edit file'),
            ('can_delete_file', 'Can delete file'),
            ('can_share_file', 'Can share file'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if self.file:
            self.size = self.file.size
            self.file_type = os.path.splitext(self.file.name)[1].lower()

            # Detect MIME type
            try:
                import magic
                self.mime_type = magic.from_buffer(self.file.read(1024), mime=True)
                self.file.seek(0)  # Reset file pointer
            except:
                self.mime_type = 'application/octet-stream'

        super().save(*args, **kwargs)

        # Assign default permissions to owner
        if is_new:
            assign_perm('can_view_file', self.owner, self)
            assign_perm('can_download_file', self.owner, self)
            assign_perm('can_edit_file', self.owner, self)
            assign_perm('can_delete_file', self.owner, self)
            assign_perm('can_share_file', self.owner, self)

    def get_file_size_display(self):
        """Return human readable file size"""
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def get_file_icon(self):
        """Return appropriate icon class based on file type"""
        image_types = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']
        document_types = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']
        spreadsheet_types = ['.xls', '.xlsx', '.csv', '.ods']
        presentation_types = ['.ppt', '.pptx', '.odp']
        video_types = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']
        audio_types = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma']
        archive_types = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
        code_types = ['.py', '.js', '.html', '.css', '.php', '.java', '.cpp', '.c']

        if self.file_type in image_types:
            return 'fas fa-image text-success'
        elif self.file_type in document_types:
            return 'fas fa-file-alt text-primary'
        elif self.file_type in spreadsheet_types:
            return 'fas fa-file-excel text-success'
        elif self.file_type in presentation_types:
            return 'fas fa-file-powerpoint text-warning'
        elif self.file_type in video_types:
            return 'fas fa-video text-danger'
        elif self.file_type in audio_types:
            return 'fas fa-music text-info'
        elif self.file_type in archive_types:
            return 'fas fa-file-archive text-secondary'
        elif self.file_type in code_types:
            return 'fas fa-code text-dark'
        else:
            return 'fas fa-file text-muted'

    def is_image(self):
        """Check if file is an image"""
        image_types = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']
        return self.file_type in image_types

    def get_thumbnail_url(self):
        """Get thumbnail URL for images"""
        if self.is_image():
            return self.file.url
        return None


class FolderPermission(models.Model):
    PERMISSION_CHOICES = [
        ('read', 'Solo Lectura'),
        ('write', 'Lectura y Escritura'),
        ('admin', 'Acceso Total'),
    ]

    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='custom_permissions',
                               verbose_name="Carpeta")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    permission_level = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='read',
                                        verbose_name="Nivel de Permiso")
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_permissions',
                                   verbose_name="Otorgado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

    class Meta:
        unique_together = ['folder', 'user']
        ordering = ['-created_at']
        verbose_name = "Permiso de Carpeta"
        verbose_name_plural = "Permisos de Carpetas"

    def __str__(self):
        return f"{self.user.username} - {self.folder.name} ({self.get_permission_level_display()})"


class FilePermission(models.Model):
    PERMISSION_CHOICES = [
        ('read', 'Solo Lectura'),
        ('write', 'Lectura y Escritura'),
        ('admin', 'Acceso Total'),
    ]

    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='custom_permissions',
                             verbose_name="Archivo")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    permission_level = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='read',
                                        verbose_name="Nivel de Permiso")
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_file_permissions',
                                   verbose_name="Otorgado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

    class Meta:
        unique_together = ['file', 'user']
        ordering = ['-created_at']
        verbose_name = "Permiso de Archivo"
        verbose_name_plural = "Permisos de Archivos"

    def __str__(self):
        return f"{self.user.username} - {self.file.name} ({self.get_permission_level_display()})"


class SharedLink(models.Model):
    PERMISSION_CHOICES = [
        ('view', 'Solo Ver'),
        ('download', 'Ver y Descargar'),
        ('edit', 'Ver, Descargar y Editar'),
    ]

    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='shared_links', verbose_name="Carpeta")
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True,
                             related_name='shared_links', verbose_name="Archivo")
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_shares',
                                  verbose_name="Compartido por")
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='received_shares', verbose_name="Compartido con")
    permission_level = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view',
                                        verbose_name="Nivel de Permiso")
    token = models.CharField(max_length=64, unique=True, verbose_name="Token")
    is_public = models.BooleanField(default=False, verbose_name="Es Público")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expira")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Enlace Compartido"
        verbose_name_plural = "Enlaces Compartidos"

    def __str__(self):
        item = self.folder or self.file
        return f"Compartido {item.name} con {self.shared_with or 'Público'}"

    def is_expired(self):
        """Check if the shared link has expired"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False

    def get_item(self):
        """Get the shared item (folder or file)"""
        return self.folder or self.file
