
from django.urls import path
from .views.siembra import *
from .views.transferencia import *

app_name = 'app_corrida'

urlpatterns = [

    path('crear_siembra_cuant', crearSiembraCuantificableView.as_view(), name='crear_siembra_cuant'),
    path('listar_siembra_cuant', listarSiembraCuantificableView.as_view(), name='listar_siembra_cuant'),

    path('reporte_siembra/<int:pk>/', reportSiembraPDF.as_view(), name='reporte_siembra'),

    path('crear_siembra_val', crearSiembraValorizableView.as_view(), name='crear_siembra_val'),
    path('listar_siembra_val', listarSiembraValorizableView.as_view(), name='listar_siembra_val'),

    path('crear_transferencia/<int:pk>/', crearTransferenciaView.as_view(), name='crear_transferencia'),
    path('listar_transferencia/', listarTransferenciaView.as_view(), name='listar_transferencia'),

]