
from django.urls import path
from app_venta.views.venta import *

app_name = 'app_venta'

urlpatterns = [

    path('sale/admin/', SaleListView.as_view(), name='sale_admin_list'),
    path('sale/admin/add/', SaleCreateView.as_view(), name='sale_admin_create'),
    path('sale/admin/delete/<int:pk>/', SaleDeleteView.as_view(), name='sale_admin_delete'),
    path('sale/admin/print/invoice/<int:pk>/', SalePrintInvoiceView.as_view(), name='sale_admin_print_invoice'),
    path('sale/client/', SaleClientListView.as_view(), name='sale_client_list'),
    path('sale/client/print/invoice/<int:pk>/', SalePrintInvoiceView.as_view(), name='sale_client_print_invoice'),

]