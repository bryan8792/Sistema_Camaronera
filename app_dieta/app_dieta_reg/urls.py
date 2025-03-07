
from django.urls import path
from .views.dieta import *

app_name = 'app_dieta'

urlpatterns = [

    # PARA LISTAR O CREAR - AÑO DE DIETA PISCINA
    path('listar/anio/', listarDietaAnioPrincipalView.as_view(), name='principal_anio'),
    path('crear/anio/', crearAnioDietaView.as_view(), name='crear_anio_dieta'),

    # PARA LISTAR - AÑO DE DIETA PRECRIA
    path('listar/anio_prec/', listarDietaAnioPrecriaView.as_view(), name='principal_anio_prec'),

    # PARA LISTAR, CREAR O EDITAR - MES DE DIETA PISCINA
    path('listar/mes/<int:anio>/', listarMesDietas, name='principal_mes'),
    path('dieta/crear/mes/', crearMesDietaView.as_view(), name='crear_mes_dieta'),

    # PARA LISTAR O EDITAR - MES DE DIETA PRECRIA
    path('listar/mes_prec/<int:anio>/', listarMesDietasPrecrias, name='principal_mes_prec'),

    # PARA LISTAR, CREAR O EDITAR - DIA DE DIETA PISCINA
    path('listar/dia/<int:pk>/', listarDiasDietas, name='principal_dia'),
    path('crear/dia/<int:pk>/', crearDiaDietaView.as_view(), name='crear_dia_dieta'),
    path('editar/dia/<int:pk>/', editarDiaDietaView.as_view(), name='modificar_dieta'),

    # PARA LISTAR, CREAR O EDITAR - DIA DE DIETA PRECRIA
    path('listar/dia_prec/<int:pk>/', listarDiasDietasPrecrias, name='principal_dia_prec'),
    path('crear/dia_prec/<int:pk>/', crearDiaDietaPrecriaView.as_view(), name='crear_dia_dieta_prec'),
    path('editar/dia_prec/<int:pk>/', editarDiaDietaPrecriaView.as_view(), name='modificar_dieta_prec'),

    # REPORTE DE LA DIETA CREADA
    path('reporte_dieta/<int:pk>/', ListarDietaPDF.as_view(), name='reporte_dieta'),

    # PARA LAS DESCIPCIONES DE LAS DIETAS
    path('listar_desc_dieta/', listarDescripcionDietaView.as_view(), name='listar_descripcion_dieta'),
    path('crear_desc_dieta/', crearDescripcionDietaView.as_view(), name='crear_descripcion_dieta'),
    path('editar_desc_dieta/<int:pk>/', actualizarDescripcionDietaView.as_view(), name='editar_descripcion_dieta'),
    path('eliminar_desc_dieta/<int:pk>/', eliminarDescripcionDietaView.as_view(), name='eliminar_descripcion_dieta'),

]