
from django.urls import path
from .views.stock import *

app_name = 'app_stock'

urlpatterns = [

    path('crearpsm/<int:pk>/', crearStockPSMView.as_view(), name='crear_stock_psm'),
    path('listarpsm/', listarStockPSMView.as_view(), name='listar_stock_psm'),

    path('listarpsmybio/', listarStockPSMyBIOView.as_view(), name='listar_stock_psmybio'),

    path('asientos-contables/', ListarAsientosContablesView.as_view(), name='listar_asientos_contables'),
    path('asientos_contables_bio/', ListarAsientosContablesBIOView.as_view(), name='listar_asientos_contables_bio'),
    path('asientos_contables_psm/', ListarAsientosContablesPSMView.as_view(), name='listar_asientos_contables_psm'),
    path('reporte_asientos_contables/', ReporteAsientosContablesView.as_view(), name='reporte_asientos_contables'),
    path('diagnostico_contable/', DiagnosticoContableView.as_view(), name='diagnostico_contable'),
    path('reporte_piscina_insumos/', ReportePiscinaInsumosView.as_view(), name='reporte_piscina_insumos'),
    path('consumo_piscina_insumos/', ConsumoPiscinaInsumosView.as_view(), name='consumo_piscina_insumos'),
    path('consumo_insumos_piscina/', ConsumoInsumosPiscinaView.as_view(), name='consumo_insumos_piscina'),

    path('listarpsmunico/<int:pk>/', listarStockUnicoPSMView.as_view(), name='listar_stock_unico_psm'),
    path('listarbiounico/<int:pk>/', listarStockUnicoBIOView.as_view(), name='listar_stock_unico_bio'),

    path('crearbio/<int:pk>/', crearStockBIOView.as_view(), name='crear_stock_bio'),
    path('listarbio/', listarStockBIOView.as_view(), name='listar_stock_bio'),

    path('crear_con_cuenta_bio/<int:empresa_id>/', CrearStockConCuentaBIOView.as_view(), name='crear_stock_con_cuenta_bio'),
    path('crear_con_cuenta_psm/<int:empresa_id>/', CrearStockConCuentaPSMView.as_view(), name='crear_stock_con_cuenta_psm'),
    path('editar_con_cuenta/<int:pk>/', EditarStockConCuentaView.as_view(),  name='editar_stock_con_cuenta'),
    path('api/cuentas_por_empresa/', get_cuentas_por_empresa, name='get_cuentas_por_empresa'),
    path('api/productos-por-empresa/', get_productos_por_empresa, name='get_productos_por_empresa'),
    path('api/stock-info/', get_stock_info,  name='get_stock_info'),

]