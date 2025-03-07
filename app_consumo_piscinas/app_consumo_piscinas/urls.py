
from django.urls import path
from .views.consumo_piscinas import *


app_name = 'app_consumo'


urlpatterns = [

    path('listar', listarConsumoView.as_view(), name='listar_consumo'),
    path('listar/consumo_piscina/<int:pk>/', listarConsumoPiscinasView.as_view(), name='listar_consumo_piscina'),
    path('listar/consumo_general/', listarConsumoGeneralView.as_view(), name='listar_consumo_general'),
    path('listar/resumen_general/', listarResumenGeneralView.as_view(), name='listar_resumen_general'),
    path('listar/resumen_general_psm/', listarResumenGeneralPSMView.as_view(), name='listar_resumen_general_psm'),
    path('listar/resumen_general_psm_linea/', listarResumenGeneralPSMLineaView.as_view(), name='listar_resumen_general_psm_linea'),
    path('listar/resumen_general_bio/', listarResumenGeneralBIOView.as_view(), name='listar_resumen_general_bio'),

]
