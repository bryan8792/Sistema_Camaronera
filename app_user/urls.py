from django.urls import path
from .views.user import *

app_name = 'app_usuario'

urlpatterns = [
    # URLs de Usuario
    path('usuario/crear/', crearUsuarioView.as_view(), name='crear_usuario'),
    path('usuario/actualizar/<int:pk>/', actualizarUsuarioView.as_view(), name='actualizar_usuario'),
    path('usuario/eliminar/<int:pk>/', eliminarUsuarioView.as_view(), name='eliminar_usuario'),
    path('usuario/listar/', listarUsuarioView.as_view(), name='listar_usuario'),
    path('usuario/detail/<int:pk>/', detalleUsuarioView.as_view(), name='detalle_usuario'),

    # URLs de Grupo
    path('grupo/crear/', crearGrupoView.as_view(), name='crear_grupo'),
    path('grupo/actualizar/<int:pk>/', actualizarGrupoView.as_view(), name='actualizar_grupo'),
    path('grupo/eliminar/<int:pk>/', eliminarGrupoView.as_view(), name='eliminar_grupo'),
    path('grupo/listar/', listarGrupoView.as_view(), name='listar_grupo'),
    path('grupo/detail/<int:pk>/', detalleGrupoView.as_view(), name='detalle_grupo'),

    # URLs de Módulo (usando los nombres correctos con mayúscula)
    path('modulo/crear/', CrearModuloView.as_view(), name='crear_modulo'),
    path('modulo/actualizar/<int:pk>/', EditarModuloView.as_view(), name='editar_modulo'),
    path('modulo/eliminar/<int:pk>/', EliminarModuloView.as_view(), name='eliminar_modulo'),
    path('modulo/listar/', ListarModuloView.as_view(), name='listar_modulo'),
    path('modulo/listar_ajax/', ListarModuloAjaxView.as_view(), name='listar_modulo_ajax'),
    path('modulo/detail/<int:pk>/', detalleModuloView.as_view(), name='detalle_modulo'),

    # URLs de Tipo de Módulo (usando los nombres correctos con mayúscula)
    path('tipo-modulo/crear/', CrearTipoModuloView.as_view(), name='crear_tipo_modulo'),
    path('tipo-modulo/listar/', ListarTipoModuloView.as_view(), name='listar_tipo_modulo'),
    path('tipo-modulo/listar_ajax/', ListarTipoModuloAjaxView.as_view(), name='listar_tipo_modulo_ajax'),
    path('tipo-modulo/editar/<int:pk>/', EditarTipoModuloView.as_view(), name='editar_tipo_modulo'),
    path('tipo-modulo/eliminar/<int:pk>/', EliminarTipoModuloView.as_view(), name='eliminar_tipo_modulo'),
]
