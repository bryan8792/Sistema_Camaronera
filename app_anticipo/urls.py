# app_anticipo/urls.py

from django.urls import path
from app_anticipo.views.anticipo import (
    AnticipoFormView,
    AnticipoListView,
    TipoPagoListView,
    FormaPagoOpcionListView
)

app_name = 'app_anticipos'

urlpatterns = [
    # Lista de anticipos
    path('listar_anticipo/', AnticipoListView.as_view(), name='anticipo_list'),

    # Formulario para crear anticipo
    path('registrar_anticipo/', AnticipoFormView.as_view(), name='anticipo_create'),

    # Formulario para editar anticipo (con ID)
    path('editar_anticipo/<int:pk>/', AnticipoFormView.as_view(), name='anticipo_edit'),

    # Gestión de tipos de pago
    path('tipos_pago/', TipoPagoListView.as_view(), name='tipo_pago_list'),

    # Gestión de formas de pago
    path('formas_pago/', FormaPagoOpcionListView.as_view(), name='forma_pago_list'),
]