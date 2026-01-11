from django.urls import path
from .views.categoria import *
from .views.producto import *
from .views.linea import *

app_name = 'app_categoria'

urlpatterns = [
    # muestrame esa vista
    path('categoria/crear/', crearCategoriaView.as_view(), name='crear_categoria'),
    path('categoria/actualizar/<int:pk>/', actualizarCategoriaView.as_view(), name='actualizar_categoria'),
    path('categoria/eliminar/<int:pk>/', eliminarCategoriaView.as_view(), name='eliminar_categoria'),
    path('categoria/listar/', listarCategoriaView.as_view(), name='listar_categoria'),

    path('producto/crear/', crearProductoView.as_view(), name='crear_producto'),
    path('producto/actualizar/<int:pk>/', actualizarProductoView.as_view(), name='actualizar_producto'),
    path('producto/eliminar/<int:pk>/', eliminarProductoView.as_view(), name='eliminar_producto'),
    path('producto/listar/', listarProductoView.as_view(), name='listar_producto'),

    path('sub_cat/crear/', crearLineaView.as_view(), name='crear_linea'),
    path('sub_cat/actualizar/<int:pk>/', actualizarLineaView.as_view(), name='actualizar_linea'),
    path('sub_cat/eliminar/<int:pk>/', eliminarLineaView.as_view(), name='eliminar_linea'),
    path('sub_cat/listar/', listarLineaView.as_view(), name='listar_linea'),

]
