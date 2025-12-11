from django.urls import path

from app_anticipo.views.anticipo import AnticipoListView, TipoPagoListView, AnticipoFormView, FormaPagoOpcionListView

app_name = 'app_anticipos'

urlpatterns = [
    path('listar_anticipo', AnticipoListView.as_view(), name='anticipo_list'),
    path('registrar_anticipo/', AnticipoFormView.as_view(), name='anticipo_form'),
    path('tipos_pago/', TipoPagoListView.as_view(), name='tipo_pago_list'),
    path('formas_pago/', FormaPagoOpcionListView.as_view(), name='forma_pago_list'),
]

