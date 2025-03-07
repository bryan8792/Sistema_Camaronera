
from django.urls import path
from .views.stock import *

app_name = 'app_stock'

urlpatterns = [

    path('stock/crearpsm/crear/<int:pk>/', crearStockPSMView.as_view(), name='crear_stock_psm'),
    path('stock/listarpsm/listar/', listarStockPSMView.as_view(), name='listar_stock_psm'),

    path('stock/listarpsmybio/listar/', listarStockPSMyBIOView.as_view(), name='listar_stock_psmybio'),

    path('stock/listarpsmunico/listar/<int:pk>/', listarStockUnicoPSMView.as_view(), name='listar_stock_unico_psm'),
    path('stock/listarbiounico/listar/<int:pk>/', listarStockUnicoBIOView.as_view(), name='listar_stock_unico_bio'),

    path('stock/crearbio/crear/<int:pk>/', crearStockBIOView.as_view(), name='crear_stock_bio'),
    path('stock/listarbio/listar/', listarStockBIOView.as_view(), name='listar_stock_bio'),

]