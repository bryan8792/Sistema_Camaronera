from django.urls import path
from .views.empresa import *
from .views.piscinas import *
from django.views.decorators.csrf import csrf_exempt

app_name = 'app_empresa'

urlpatterns = [

    path('empresa/listar/', listarEmpresaView.as_view(), name='listar_empresa'),
    path('empresa/crear/', crearEmpresaView.as_view(), name='crear_empresa'),
    path('empresa/actualizar/<int:pk>/', actualizarEmpresaView.as_view(), name='actualizar_empresa'),
    path('empresa/eliminar/<int:pk>/', eliminarEmpresaView.as_view(), name='eliminar_empresa'),

    path('piscina/listar/', listarPiscinasView.as_view(), name='listar_piscinas'),
    path('piscina/crear/', crearPiscinaView.as_view(), name='crear_piscinas'),
    path('piscina/actualizar/<int:pk>/', actualizarPiscinaView.as_view(), name='actualizar_piscinas'),
    path('piscina/eliminar/<int:pk>/', eliminarPiscinaView.as_view(), name='eliminar_piscinas'),

]
