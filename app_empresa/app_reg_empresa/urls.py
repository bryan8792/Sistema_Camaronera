from django.urls import path
from .views.crear_transaccion import *
from .views.debug_view import *
from .views.empresa import *
from .views.piscinas import *

app_name = 'app_empresa'

urlpatterns = [

    path('empresa/listar/', listarEmpresaView.as_view(), name='listar_empresa'),
    path('empresa/crear/', crearEmpresaView.as_view(), name='crear_empresa'),
    path('empresa/actualizar/<int:pk>/', actualizarEmpresaView.as_view(), name='actualizar_empresa'),
    path('empresa/eliminar/<int:pk>/', eliminarEmpresaView.as_view(), name='eliminar_empresa'),
    path('dashboard_bio', listarDashboardBIO.as_view(), name='dashboard_bio'),

    path('piscina/listar/', listarPiscinasView.as_view(), name='listar_piscinas'),
    path('piscina/crear/', crearPiscinaView.as_view(), name='crear_piscinas'),
    path('piscina/actualizar/<int:pk>/', actualizarPiscinaView.as_view(), name='actualizar_piscinas'),
    path('piscina/eliminar/<int:pk>/', eliminarPiscinaView.as_view(), name='eliminar_piscinas'),

    # Rutas para costo-utilidad por hectárea
    path('costo-utilidad-hectarea/', CostoUtilidadHectareaView.as_view(), name='costo_utilidad_hectarea'),
    path('costo-utilidad-hectarea/api/', CostoUtilidadHectareaAPIView.as_view(), name='costo_utilidad_hectarea_api'),

    # Rutas para tipos de costo
    path('tipos-costo/', TipoCostoListView.as_view(), name='tipo_costo_list'),
    path('tipos-costo/crear/', TipoCostoCreateView.as_view(), name='tipo_costo_create'),
    path('tipos-costo/editar/<int:pk>/', TipoCostoUpdateView.as_view(), name='tipo_costo_update'),
    path('tipos-costo/eliminar/<int:pk>/', TipoCostoDeleteView.as_view(), name='tipo_costo_delete'),

    # Rutas para costos operativos
    path('costos-operativos/', CostoOperativoListView.as_view(), name='costo_operativo_list'),
    path('costos-operativos/crear/', CostoOperativoCreateView.as_view(), name='costo_operativo_create'),
    path('costos-operativos/editar/<int:pk>/', CostoOperativoUpdateView.as_view(), name='costo_operativo_update'),
    path('costos-operativos/eliminar/<int:pk>/', CostoOperativoDeleteView.as_view(), name='costo_operativo_delete'),

    # Rutas para producciones
    path('producciones/', ProduccionListView.as_view(), name='produccion_list'),
    path('producciones/crear/', ProduccionCreateView.as_view(), name='produccion_create'),
    path('producciones/editar/<int:pk>/', ProduccionUpdateView.as_view(), name='produccion_update'),
    path('producciones/eliminar/<int:pk>/', ProduccionDeleteView.as_view(), name='produccion_delete'),

    # Rutas para ciclos
    path('ciclos/', CicloListView.as_view(), name='ciclo_list'),
    path('ciclos/crear/', CicloCreateView.as_view(), name='ciclo_create'),
    path('ciclos/editar/<int:pk>/', CicloUpdateView.as_view(), name='ciclo_update'),
    path('ciclos/eliminar/<int:pk>/', CicloDeleteView.as_view(), name='ciclo_delete'),

    # APIs
    path('api/ciclos-por-piscina/', CiclosPorPiscinaView.as_view(), name='ciclos_por_piscina'),
    path('api/piscina-info/', PiscinaInfoView.as_view(), name='piscina_info'),
    path('cargar-datos-iniciales/', cargar_datos_iniciales, name='cargar_datos_iniciales'),

    # Rutas de depuración
    path('debug/template/', DebugTemplateView.as_view(), name='debug_template'),
    path('debug/blocks/', DebugBlocksView.as_view(), name='debug_blocks'),
    path('debug/costo-utilidad-hectarea/', DebugCostoUtilidadHectareaView.as_view(), name='debug_costo_utilidad_hectarea'),
    path('debug/costos-operativos/', DebugCostoOperativoListView.as_view(), name='debug_costo_operativo_list'),
    path('debug/producciones/', DebugProduccionListView.as_view(), name='debug_produccion_list'),

    path('desglose-costos/', DesgloseCostosView.as_view(), name='desglose_costos'),

]
