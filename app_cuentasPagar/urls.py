from django.urls import path
from app_cuentasPagar.views.cuentasPagar import *

app_name = 'app_cuentasPagar'

urlpatterns = [

    path('debts/pay/', DebtsPayListView.as_view(), name='debts_pay_list'),
    path('debts/pay/add/', DebtsPayCreateView.as_view(), name='debts_pay_create'),
    path('debts/pay/delete/<int:pk>/', DebtsPayDeleteView.as_view(), name='debts_pay_delete'),

]
