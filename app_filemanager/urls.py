from django.urls import path
from .views.filemanager import (
    DashboardView,
    FileListView,
    FileUploadView,
    SingleFileUploadView,
    FolderCreateView,
    FolderDetailView,
    FileDownloadView,
    FileDeleteView,
    FolderDeleteView,
    FolderPermissionListView,
    FolderPermissionCreateView,
    MySharedFoldersView,
    SharedWithMeView,
    FolderEditView,
    ajax_file_upload,  # Importar función en lugar de clase
    ajax_move,
    user_search,
    folder_permissions,
    folder_permission_create,
    folder_permission_update,
    folder_permission_delete,
    bulk_revoke_permissions,
)

app_name = 'app_filemanager'

urlpatterns = [
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),

    # File management
    path('files/', FileListView.as_view(), name='file_list'),
    path('files/folder/<int:folder_id>/', FileListView.as_view(), name='folder_detail'),
    path('upload/', FileUploadView.as_view(), name='file_upload'),
    path('upload/single/', SingleFileUploadView.as_view(), name='single_file_upload'),

    # AJAX endpoints
    path('ajax/upload/', ajax_file_upload, name='ajax_file_upload'),  # Usar función
    path('ajax/move/', ajax_move, name='ajax_move'),
    path('ajax/user-search/', user_search, name='user_search'),

    # Folder management
    path('folder/create/', FolderCreateView.as_view(), name='folder_create'),
    path('folder/<int:pk>/', FolderDetailView.as_view(), name='folder_detail'),
    path('folder/<int:pk>/edit/', FolderEditView.as_view(), name='folder_edit'),
    path('folder/<int:pk>/delete/', FolderDeleteView.as_view(), name='folder_delete'),

    # File operations
    path('file/<int:pk>/download/', FileDownloadView.as_view(), name='file_download'),
    path('file/<int:pk>/delete/', FileDeleteView.as_view(), name='file_delete'),

    # Permissions
    path('folder/<int:folder_id>/permissions/', folder_permissions, name='folder_permissions'),
    path('folder/<int:folder_id>/permissions/create/', folder_permission_create, name='folder_permission_create'),
    path('folder/<int:folder_id>/permissions/<int:perm_id>/update/', folder_permission_update,
         name='folder_permission_update'),
    path('folder/<int:folder_id>/permissions/<int:perm_id>/delete/', folder_permission_delete,
         name='folder_permission_delete'),
    path('folder/<int:folder_id>/permissions/bulk-revoke/', bulk_revoke_permissions, name='bulk_revoke_permissions'),

    # Shared folders
    path('shared/', MySharedFoldersView.as_view(), name='my_shared_folders'),
    path('shared-with-me/', SharedWithMeView.as_view(), name='shared_with_me'),
]
