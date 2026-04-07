from django.urls import path
from app_factura_detalle.views.factura_gasto import *
from .views.recibo import *
from .views.planCuentas import *
from .views.procesosATS import *

app_name = 'app_planCuentas'

urlpatterns = [

    # REQUISITOS PARA EL MODULO PLAN DE CUENTAS
    # BIO
    path('crearPlanBIO/', crearPlanCuentaView.as_view(), name='crear_planCuenta_bio'),
    path('actualizarPlanBIO/<int:pk>/', actualizarPlanCuentaView.as_view(), name='actualizar_planCuenta_bio'),
    path('eliminarPlanBIO/<int:pk>/', eliminarPlanCuentaView.as_view(), name='eliminar_planCuenta_bio'),
    path('listarPlanBIO/', listarPlanCuentaBIOView.as_view(), name='listar_planCuenta_BIO'),
    path('export/excelBIO/', PlanExportExcelBIOView.as_view(), name='plan_export_excel_bio'),
    # PSM
    path('crearPlanPSM/', crearPlanCuentaPSMView.as_view(), name='crear_planCuenta_psm'),
    path('actualizarPlanPSM/<int:pk>/', actualizarPlanCuentaPSMView.as_view(), name='actualizar_planCuenta_psm'),
    path('eliminarPlanPSM/<int:pk>/', eliminarPlanCuentaPSMView.as_view(), name='eliminar_planCuenta_psm'),
    path('listarPlanPSM/', listarPlanCuentaPSMView.as_view(), name='listar_planCuenta_PSM'),
    path('export/excelPSM/', PlanExportExcelPSMView.as_view(), name='plan_export_excel_psm'),

    # REQUISITOS PARA EL MODULO TRANSACCION DEL PLAN DE CUENTAS
    path('transaccionpsm/listar/', listarTransaccionPlanView.as_view(), name='listar_transaccionPlan'),
    path('transaccionbio/listar/', listarTransaccionPlanBIOView.as_view(), name='listar_transaccionPlan_bio'),
    path('reporte/pdf/<int:pk>/', TransaccionInvoicePdfView.as_view(), name='reporte_pdf'),
    path('transaccion/crear/', crearTransaccionPlanView.as_view(), name='crear_transaccionPlan'),

    path('transaccionbio/crear/', crearTransaccionPlanBIOView.as_view(), name='crear_transaccionPlan_bio'),

    path('transaccion/editar/<int:pk>/', editarTransaccionPlanView.as_view(), name='editar_transaccionPlan'),
    path('transaccionbio/editar/<int:pk>/', editarTransaccionPlanBIOView.as_view(), name='editar_transaccionPlan_bio'),

    # REQUISITOS PARA EL MODULO TRANSACCION EN FACTURA DE GASTO EN EL PLAN DE CUENTAS
    path('fact_gasto_psm/listar/', listarFacturaGastoPSMView.as_view(), name='listar_fact_gasto_psm'),
    path('fact_gasto_bio/listar/', listarFacturaGastoBIOView.as_view(), name='listar_fact_gasto_bio'),
    path('fact_gasto/crear/', crearFacturaGastoView.as_view(), name='crear_fact_gasto'),

    path('fact_gasto_bio/crear/', crearFacturaGastoBIOView.as_view(), name='crear_fact_gasto_bio'),

    path('fact_gasto/editar/<int:pk>/', editarFacturaGastoView.as_view(), name='editar_fact_gasto'),
    path('fact_gasto_bio/editar/<int:pk>/', editarFacturaGastoBIOView.as_view(), name='editar_fact_gasto_bio'),
    # path('fact_gasto/eliminar/<int:pk>/', editarTransaccionPlanView.as_view(), name='eliminar_fact_gasto'),

    # REQUISITOS PARA EL MODULO BALANCE DE COMPROBACION DEL PLAN DE CUENTAS
    path('balancepsm/listar/', listarBalancePlanView.as_view(), name='listar_balancePlan_psm'),
    path('balancebio/listar/', listarBalancePlanBIOView.as_view(), name='listar_balancePlan_bio'),
    # path('transaccion/crear/', crearTransaccionPlanView.as_view(), name='crear_transaccionPlan'),
    # path('transaccion/editar/<int:pk>/', editarTransaccionPlanView.as_view(), name='editar_transaccionPlan'),

    # REQUISITOS PARA EL MODULO TRANSACCION DEL PLAN DE CUENTAS
    path('mayorizacion_psm/listar/', listarMayorPlanView.as_view(), name='listar_mayorPlan_psm'),
    path('mayorizacion_bio/listar/', listarMayorPlanViewBIO.as_view(), name='listar_mayorPlan_bio'),

    path('diario_acumulado_psm/', DiarioGeneralAcumuladoPSMView.as_view(), name='diario_general_acumulado_psm'),
    path('diario_acumulado_bio/', DiarioGeneralAcumuladoBIOView.as_view(), name='diario_general_acumulado_bio'),

    # Recibo
    path('receipt/listar/', ReceiptListView.as_view(), name='recibo_listar'),
    path('receipt/crear/', ReceiptCreateView.as_view(), name='recibo_crear'),
    path('receipt/actualizar/<int:pk>/', ReceiptUpdateView.as_view(), name='recibo_actualizar'),
    path('receipt/eliminar/<int:pk>/', ReceiptDeleteView.as_view(), name='recibo_eliminar'),

    # PrintExpenseInvoiceView
    path('factura_gasto/print/invoice/<int:pk>/', PrintExpenseInvoiceView.as_view(),
         name='factura_gasto_print_invoice'),
    path('factura_gasto_bio/print/invoice_bio/<int:pk>/', PrintExpenseInvoiceBIOView.as_view(),
         name='factura_gasto_bio_print_invoice'),

    # Menú principal
    path('menu_ats/', ATSMenuView.as_view(), name='menu_ats'),

    # Generación de XML
    path('generar_xml/', ATSGenerarXMLView.as_view(), name='generar_xml'),

    # Importar datos
    path('importar_compras/', ATSImportarComprasView.as_view(), name='importar_compras'),
    path('importar_ventas/', ATSImportarVentasView.as_view(), name='importar_ventas'),
    path('importar_xml/', ATSImportarXMLView.as_view(), name='importar_xml'),

    # Revisión de datos
    path('revision_datos/', ATSRevisionDatosView.as_view(), name='revision_datos'),

    # Carpeta XML
    path('carpeta_xml/', ATSCarpetaXMLView.as_view(), name='carpeta_xml'),

    # Libro Mayor Detalle
    path('libro_mayor/detalle/', LibroMayorDetalleView.as_view(), name='libro_mayor_detalle'),

    # Estado de Resultados
    path('estado_resultados/', EstadoResultadosView.as_view(), name='estado_resultados'),

    # Balance General
    path('balance_general/', BalanceGeneralView.as_view(), name='balance_general'),

    # ESTADO DE RESULTADOS
    path('estado_resultados_psm/', EstadoResultadosView.as_view(), name='estado_resultados_psm'),
    path('estado_resultados_bio/', EstadoResultadosBIOView.as_view(), name='estado_resultados_bio'),

    # BALANCE GENERAL
    path('balance_general_psm/', BalanceGeneralView.as_view(), name='balance_general_psm'),
    path('balance_general_bio/', BalanceGeneralBIOView.as_view(), name='balance_general_bio'),

    # CIERRE CONTABLE
    path('cierre_contable/', CierreContableView.as_view(), name='cierre_contable'),

    # RATIOS FINANCIEROS
    path('ratios_financieros/', RatiosFinancierosView.as_view(), name='ratios_financieros'),

]
