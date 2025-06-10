
from django.urls import path
from .views.cliente import *

app_name = 'app_cliente'

urlpatterns = [
   # muestrame esa vista
    path('cliente/crear/', ClienteCreateView.as_view(), name='crear_cliente'),
    path('cliente/actualizar/<int:pk>/', ClienteUpdateView.as_view(), name='actualizar_cliente'),
    path('cliente/eliminar/<int:pk>/', ClienteDeleteView.as_view(), name='eliminar_cliente'),
    path('cliente/listar/', ClienteListView.as_view(), name='listar_cliente'),
]