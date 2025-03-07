
from django.urls import path
from .views.stock_directo import *

app_name = 'app_stock_directo'

urlpatterns = [

    # path('stock/crearpsm/crear/', crearStockPSMView.as_view(), name='crear_stock_psm'),
    path('stock/crearpsm_directo/crear/<int:pk>/', crearStockPSMDirectoView.as_view(), name='crear_stock_directo_psm'),
    path('stock/listarpsm_directo/listar/', listarStockPSMDirectoView.as_view(), name='listar_stock_directo_psm'),

    path('stock/listarpsmunico_directo/listar/<int:pk>/', listarStockUnicoPSMDirectoView.as_view(), name='listar_stock_directo_unico_psm'),
    path('stock/listarbiounico_directo/listar/<int:pk>/', listarStockUnicoBIODirectoView.as_view(), name='listar_stock_directo_unico_bio'),

    #path('stock/crearbio/crear/', crearStockBIOView.as_view(), name='crear_stock_bio'),
    path('stock/crearbio_directo/crear/<int:pk>/', crearStockBIODirectoView.as_view(), name='crear_stock_directo_bio'),
    path('stock/listarbio_directo/listar/', listarStockBIODirectoView.as_view(), name='listar_stock_directo_bio'),

]