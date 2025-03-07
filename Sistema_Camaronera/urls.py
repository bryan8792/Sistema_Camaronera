"""Sistema_Camaronera URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.conf import settings
from Sistema_Camaronera import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from app_login.views.login import loginFormView
from app_template.views.template import IndexView

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='inicio_dashboard'),
    path('login/', include('app_login.urls')),
    path('inventario/', include('app_inventario.app_categoria.urls')),
    path('proveedor/', include('app_proveedor.urls')),
    path('stock/', include('app_stock.app_detalle_stock.urls')),
    path('stock_directo/', include('app_stock_directo.urls')),
    path('empresa/', include('app_empresa.app_reg_empresa.urls')),
    path('dieta/', include('app_dieta.app_dieta_reg.urls')),
    path('seguimiento_consumo/', include('app_consumo_piscinas.app_consumo_piscinas.urls')),
    path('corrida/', include('app_corrida.urls')),
    path('factura/', include('app_factura_detalle.urls')),
    path('kardex/', include('app_kardex.urls')),
    path('planCuentas/', include('app_contabilidad_planCuentas.urls', namespace='planCuentas')),
    path('usuario/', include('app_user.urls')),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
