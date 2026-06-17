from django.urls import path
from .views.segLineal import *

app_name = 'app_seguimiento_lineal'

urlpatterns = [

    path('listar_seguimiento/', listarSeguimientoView.as_view(), name='listar_seguimiento'),
    path('listar_seguimiento_det/det_piscina/<int:pk>/', listarSeguimientoPiscinasView.as_view(), name='listar_seguimiento_det_piscina'),
    path('crear/transf_larva/', CrearTransferenciaLarvaView.as_view(), name='crear_transf_larva'),
    path('dashboard_transferencia/', DashboardTransferenciaLarvaView.as_view(), name='dashboard_transferencia'),
    path('listar_transferencia/', listarTransferenciaLarvaView.as_view(), name='listar_transferencia'),
    path('detalle/<int:pk>/', detalleTransferenciaLarvaView.as_view(), name='detalle_transferencia'),
    path('editar/<int:pk>/', editarTransferenciaLarvaView.as_view(), name='editar_transferencia'),
    path('eliminar/<int:pk>/', eliminarTransferenciaLarvaView.as_view(), name='eliminar_transferencia'),

]
