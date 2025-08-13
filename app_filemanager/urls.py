from django.urls import path
from app_filemanager.views.filemanager import *

app_name = 'app_filemanager'

urlpatterns = [
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),

    # File management URLs
    path('files/', FileListView.as_view(), name='file_list'),
    path('files/folder/<int:folder_id>/', FileListView.as_view(), name='file_list_folder'),
    path('folder/<int:pk>/', FolderDetailView.as_view(), name='folder_detail'),

    # Upload and create
    path('upload/', FileUploadView.as_view(), name='file_upload'),
    path('upload/single/', SingleFileUploadView.as_view(), name='single_file_upload'),
    path('ajax-upload/', AjaxFileUploadView.as_view(), name='ajax_file_upload'),
    path('create-folder/', FolderCreateView.as_view(), name='folder_create'),

    # Download and delete
    path('file/<int:pk>/download/', FileDownloadView.as_view(), name='file_download'),
    path('file/<int:pk>/delete/', FileDeleteView.as_view(), name='file_delete'),
    path('folder/<int:pk>/delete/', FolderDeleteView.as_view(), name='folder_delete'),

    # Permissions
    path('folder/<int:folder_id>/permissions/', FolderPermissionListView.as_view(), name='folder_permissions'),
    path('folder/<int:folder_id>/permissions/grant/', FolderPermissionCreateView.as_view(),
         name='folder_permission_create'),

    # AJAX endpoints
    path('users/search/', UserSearchView.as_view(), name='user_search'),

    # ... tus otras rutas ...
    path("user-search/", user_search, name="user_search"),

    # Permisos
    path("folder/<int:folder_id>/permissions/create/", folder_permission_create, name="folder_permission_create"),
    path("folder/<int:folder_id>/permissions/", folder_permissions, name="folder_permissions"),
    path("folder/<int:folder_id>/permissions/update/<int:perm_id>/", folder_permission_update, name="folder_permission_update"),
    path("folder/<int:folder_id>/permissions/delete/<int:perm_id>/", folder_permission_delete, name="folder_permission_delete"),

    path("move/", ajax_move, name="ajax_move"),

    # path("upload/ajax/", ajax_file_upload, name="ajax_file_upload"),


]
