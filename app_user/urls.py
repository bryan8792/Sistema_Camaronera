from django.urls import path
from .views.user import *

app_name = 'app_usuario'

urlpatterns = [

    path('usuario/crear/', crearUsuarioView.as_view(), name='crear_usuario'),
    path('usuario/actualizar/<int:pk>/', actualizarUsuarioView.as_view(), name='actualizar_usuario'),
    path('usuario/eliminar/<int:pk>/', eliminarUsuarioView.as_view(), name='eliminar_usuario'),
    path('usuario/listar/', listarUsuarioView.as_view(), name='listar_usuario')
]