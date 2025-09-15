
from django.urls import path
from .views.stock import *

app_name = 'app_stock'

urlpatterns = [

    path('crearpsm/<int:pk>/', crearStockPSMView.as_view(), name='crear_stock_psm'),
    path('listarpsm/', listarStockPSMView.as_view(), name='listar_stock_psm'),

    path('listarpsmybio/', listarStockPSMyBIOView.as_view(), name='listar_stock_psmybio'),

    path('listarpsmunico/<int:pk>/', listarStockUnicoPSMView.as_view(), name='listar_stock_unico_psm'),
    path('listarbiounico/<int:pk>/', listarStockUnicoBIOView.as_view(), name='listar_stock_unico_bio'),

    path('crearbio/<int:pk>/', crearStockBIOView.as_view(), name='crear_stock_bio'),
    path('listarbio/', listarStockBIOView.as_view(), name='listar_stock_bio'),

]