
from django.urls import path
from app_cuentasCobrar.views.cuentasCobrar import *

app_name = 'app_cuentasCobrar'

urlpatterns = [

    path('ctas/collect/', CtasCollectListView.as_view(), name='ctas_collect_list'),
    path('ctas/collect/add/', CtasCollectCreateView.as_view(), name='ctas_collect_create'),
    path('ctas/collect/delete/<int:pk>/', CtasCollectDeleteView.as_view(), name='ctas_collect_delete'),

]