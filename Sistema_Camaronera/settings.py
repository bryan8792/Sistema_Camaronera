"""
Django settings for Sistema_Camaronera project.
Configurado para Multi-Tenant con django-tenants
"""

import os
import Sistema_Camaronera.db as db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '$!^h(1kmmw59!vm2zm@_cg6_2pt7ai04bon35z=kst_p4sq-t='


# IMPORTANTE: Agregar tu dominio y subdominios
ALLOWED_HOSTS = ['*', '.localhost', 'localhost', '127.0.0.1', '.tudominio.com', 'lvh.me', '.lvh.me']

# ============ CONFIGURACION MULTI-TENANT ============
DEBUG = True
if DEBUG:
    DOMAIN = "localhost"
    # DOMAIN_PORT = ':8000'
else:
    DOMAIN = 'dominio.com'
    # DOMAIN_PORT = ''


DEFAULT_SCHEMA = 'public'

PUBLIC_SCHEMA_NAME = "public"

# Modelos de tenant (OBLIGATORIO)
TENANT_MODEL = 'app_tenant.Scheme'
TENANT_DOMAIN_MODEL = 'app_tenant.Domain'

# Router de base de datos (OBLIGATORIO)
DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)

# ============ APPS COMPARTIDAS (esquema public) ============
# Estas apps se comparten entre TODOS los tenants
SHARED_APPS = [
    'django_tenants',  # DEBE ir primero
    'app_tenant',      # Tu app de tenant

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tu user debe estar compartido
    'app_user',

    # Third party apps compartidas
    'widget_tweaks',
    'guardian',
    'crispy_forms',
    'crispy_bootstrap5',

    # Tu app de usuarios (compartida para que puedan loguearse)
    # 'app_user',
    'app_empresa.app_reg_empresa',
    # 'app_proveedor',
]

# ============ APPS POR TENANT (cada empresa tiene su propia data) ============
TENANT_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # Tu User
    'app_user',

    # Todas tus apps de negocio
    'app_proveedor',
    'app_login',
    'app_corrida',
    'app_auditoria',
    'app_reportes',
    'app_factura_detalle',
    'app_contabilidad_planCuentas',
    'app_inventario.app_categoria',
    'app_inventario.app_producto',
    'app_stock.app_detalle_stock.apps.AppDetalleStockConfig',
    'app_empresa.app_reg_empresa',
    'app_dieta.app_dieta_reg',
    'app_cliente',
    'app_venta',
    'app_notaCredito',
    'app_compra',
    'app_cuentasCobrar',
    'app_filemanager',
    'app_anticipo',
    'app_empresa.app_piscinas',
    'app_costoutilidad',
]

# Combinar apps (NO modificar esta linea)
INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

# ============ MIDDLEWARE (EL ORDEN ES CRITICO) ============
MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',  # DEBE ser PRIMERO
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
]

ROOT_URLCONF = 'Sistema_Camaronera.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app_tenant.context_processors.empresa_actual',
                'app_tenant.context_processors.domain_global',
                # 'app_user.context_processors.menu_modulos',
            ],
        },
    },
]

WSGI_APPLICATION = 'Sistema_Camaronera.wsgi.application'

# Base de datos
DATABASES = db.POSTGRESQL

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_L10N = False
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Login
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

AUTH_USER_MODEL = 'app_user.User'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

GROUPS = {
    'secretaria': 2,
    'client': 3,
}

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024

# Guardian settings
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

# Crispy forms settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"