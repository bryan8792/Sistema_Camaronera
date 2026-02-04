from django.urls import path
from app_retencion.views.retencion import RetentionCreateView, RetentionListView

app_name = 'app_retencion'

urlpatterns = [
    path('retention/create/', RetentionCreateView.as_view(), name='retention_create'),
    path('retention/list/', RetentionListView.as_view(), name='retention_list'),
]
