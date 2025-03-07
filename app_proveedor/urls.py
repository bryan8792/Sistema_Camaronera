from django.urls import path
from .views.proveedor import *
from django.views.decorators.csrf import csrf_exempt

app_name = 'app_proveedor'

urlpatterns = [

    path('proveedor/listar/', listarProveedorView.as_view(), name='listar_proveedor'),
    path('proveedor/crear/', crearProveedorView.as_view(), name='crear_proveedor'),
    path('proveedor/actualizar/<int:pk>/', actualizarProveedorView.as_view(), name='actualizar_proveedor'),
    path('proveedor/eliminar/<int:pk>/', eliminarProveedorView.as_view(), name='eliminar_proveedor'),

]