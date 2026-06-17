from django.urls import path
from app_consumo.views import views_kardex
from app_consumo.views.views_kardex import KardexBodegaGeneralView, KardexBodegaView

app_name = 'app_consumo_kardex'

urlpatterns = [
    path('kardex_bodega/', KardexBodegaView.as_view(), name='kardex_bodega'),
    path('kardex_bodega_general/', KardexBodegaGeneralView.as_view(), name='kardex_bodega_general'),
]