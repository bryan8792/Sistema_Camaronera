from django.urls import path
from .views.filemanager import (
    DashboardView, FileListView, FileUploadView, SingleFileUploadView,
    FolderCreateView, FolderDetailView, FolderDeleteView, FileDeleteView,
    FileDownloadView, AjaxFileUploadView, FolderPermissionListView,
    FolderPermissionCreateView, UserSearchView, folder_permissions,
    folder_permission_create, user_search, ajax_file_upload, ajax_move,
    folder_permission_update, folder_permission_delete, bulk_revoke_permissions,
    MySharedFoldersView, SharedWithMeView, FolderEditView
)

app_name = 'app_filemanager'

urlpatterns = [
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),

    # File management
    path('files/', FileListView.as_view(), name='file_list'),
    path('files/folder/<int:folder_id>/', FileListView.as_view(), name='file_list_folder'),
    path('upload/', FileUploadView.as_view(), name='file_upload'),
    path('upload/single/', SingleFileUploadView.as_view(), name='single_file_upload'),
    path('file/<int:pk>/download/', FileDownloadView.as_view(), name='file_download'),
    path('file/<int:pk>/delete/', FileDeleteView.as_view(), name='file_delete'),

    # Folder management
    path('folder/create/', FolderCreateView.as_view(), name='folder_create'),
    path('folder/<int:pk>/', FolderDetailView.as_view(), name='folder_detail'),
    path('folder/<int:pk>/edit/', FolderEditView.as_view(), name='folder_edit'),
    path('folder/<int:pk>/delete/', FolderDeleteView.as_view(), name='folder_delete'),

    # Permissions
    path('folder/<int:folder_id>/permissions/', folder_permissions, name='folder_permissions'),
    path('folder/<int:folder_id>/permissions/create/', folder_permission_create, name='folder_permission_create'),
    path('folder/<int:folder_id>/permissions/<int:perm_id>/update/', folder_permission_update,
         name='folder_permission_update'),
    path('folder/<int:folder_id>/permissions/<int:perm_id>/delete/', folder_permission_delete,
         name='folder_permission_delete'),
    path('folder/<int:folder_id>/permissions/bulk-revoke/', bulk_revoke_permissions, name='bulk_revoke_permissions'),

    # Sharing views
    path('my-shared/', MySharedFoldersView.as_view(), name='my_shared_folders'),
    path('shared-with-me/', SharedWithMeView.as_view(), name='shared_with_me'),

    # AJAX endpoints
    path('ajax/upload/', ajax_file_upload, name='ajax_file_upload'),
    path('ajax/move/', ajax_move, name='ajax_move'),
    path('ajax/user-search/', user_search, name='user_search'),

    # Legacy AJAX (mantener compatibilidad)
    path('ajax/file-upload/', AjaxFileUploadView.as_view(), name='ajax_file_upload_legacy'),
    path('ajax/users/', UserSearchView.as_view(), name='user_search_legacy'),
]
