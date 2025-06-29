
from django.urls import path
from .views.cliente import *

app_name = 'app_cliente'

urlpatterns = [
    path('crear/', ClientCreateView.as_view(), name='crear_cliente'),
    path('actualizar/<int:pk>/', ClientUpdateView.as_view(), name='actualizar_cliente'),
    path('eliminar/<int:pk>/', ClientDeleteView.as_view(), name='eliminar_cliente'),
    path('listar/', ClientListView.as_view(), name='listar_cliente'),
    path('update/profile/', ClientUpdateProfileView.as_view(), name='client_update_profile'),
]