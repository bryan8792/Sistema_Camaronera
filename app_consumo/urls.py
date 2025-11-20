from django.urls import path
from app_consumo.views import views_kardex

app_name = 'app_consumo_kardex'

urlpatterns = [
    path('kardex_bodega/', views_kardex.KardexBodegaView.as_view(), name='kardex_bodega'),
    path('kardex_bodega_general/', views_kardex.KardexBodegaGeneralView.as_view(), name='kardex_bodega_general'),
]