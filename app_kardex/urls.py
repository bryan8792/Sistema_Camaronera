from django.urls import path
from .views.kardex import *

app_name = 'app_kardex'

urlpatterns = [

    path('stock/kardexgeneral/listar/', listarKardexGeneralView.as_view(), name='listar_kardex_general'),
    path('stock/kardexdetallado/listar/', listarKardexDetalladoView.as_view(), name='listar_kardex_detallado'),
    path('stock/kardexmovpsm/listar/', listarKardexMovimientosPSMView.as_view(), name='listar_kardex_movimientos_psm'),
    path('stock/kardexmovbio/listar/', listarKardexMovimientosBIOView.as_view(), name='listar_kardex_movimientos_bio'),
    path('stock/kardexproductos/listar/', listarKardexProductosView.as_view(), name='listar_kardex_productos'),

]