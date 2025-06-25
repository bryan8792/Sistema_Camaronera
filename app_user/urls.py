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

    # URLs de Módulo
    path('modulo/crear/', crearModuloView.as_view(), name='crear_modulo'),
    path('modulo/actualizar/<int:pk>/', actualizarModuloView.as_view(), name='actualizar_modulo'),
    path('modulo/eliminar/<int:pk>/', eliminarModuloView.as_view(), name='eliminar_modulo'),
    path('modulo/listar/', listarModuloView.as_view(), name='listar_modulo'),

    # URLs de Tipo de Módulo
    path('tipo-modulo/crear/', crearTipoModuloView.as_view(), name='crear_tipo_modulo'),
    path('tipo-modulo/listar/', listarTipoModuloView.as_view(), name='listar_tipo_modulo'),
]