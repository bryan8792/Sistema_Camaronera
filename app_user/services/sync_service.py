from django.contrib.auth.models import Group
from django_tenants.utils import schema_context
from app_user.models import Modulo, TipoModulo, GrupoModulo


def sync_tenant_modulos(schema_name):

    estructura = {
        "Seguridad": {
            "Usuarios": "app_user:listar_usuario",
            "Grupos": "app_user:listar_grupo",
            "Módulos del Sistema": "app_user:listar_modulo",
            "Tipos de Módulos": "app_user:listar_tipo_modulo",
        },
        "Inventario": {
            "Inventario": "app_categoria:listar_categoria",
            "Proveedor": "app_proveedor:listar_proveedor",
            "Stock": "app_detalle_stock:listar_stock_bio",
            "Stock Directo": "app_stock_directo:listar_stock_directo_bio",
            "Kardex": "app_kardex:listar_kardex_general",
        },
        "Producción": {
            "Dieta": "app_dieta_reg:listar_dieta",
            "Seguimiento Consumo": "app_consumo_piscinas:listar_consumo",
            "Corrida": "app_corrida:listar_corrida",
        },
        "Facturación": {
            "Factura": "app_factura_detalle:listar_factura",
            "Clientes": "app_cliente:listar_cliente",
            "Ventas": "app_venta:listar_venta",
            "Nota Crédito": "app_notaCredito:listar_notaCredito",
            "Anticipo": "app_anticipo:listar_anticipo",
        },
        "Contabilidad": {
            "Plan de Cuentas": "app_contabilidad_planCuentas:listar_plan_cuentas",
            "Cuentas por Cobrar": "app_cuentasCobrar:listar_cuentasCobrar",
            "Cuentas por Pagar": "app_cuentasPagar:listar_cuentasPagar",
        },
        "Sistema": {
            "Empresa": "app_reg_empresa:listar_empresa",
            "File Manager": "app_filemanager:dashboard",
        }
    }

    with schema_context(schema_name):

        modulos_creados = []
        orden_tipo = 1

        for nombre_tipo, modulos in estructura.items():

            tipo, _ = TipoModulo.objects.get_or_create(
                nombre=nombre_tipo,
                defaults={"orden": orden_tipo}
            )

            orden_modulo = 1

            for nombre_modulo, url_name in modulos.items():

                modulo, _ = Modulo.objects.get_or_create(
                    nombre=nombre_modulo,
                    defaults={
                        "url": url_name,
                        "tipo": tipo,
                        "orden": orden_modulo,
                        "activo": True
                    }
                )

                modulo.url = url_name
                modulo.tipo = tipo
                modulo.orden = orden_modulo
                modulo.activo = True
                modulo.save()

                modulos_creados.append(nombre_modulo)
                orden_modulo += 1

            orden_tipo += 1

        # Eliminar módulos que ya no estén definidos
        Modulo.objects.exclude(nombre__in=modulos_creados).delete()

        # Crear grupo ADMIN
        grupo, _ = Group.objects.get_or_create(name="ADMIN")

        # Permisos completos
        for modulo in Modulo.objects.all():

            obj, _ = GrupoModulo.objects.get_or_create(
                grupo=grupo,
                modulo=modulo
            )

            obj.can_view = True
            obj.can_add = True
            obj.can_change = True
            obj.can_delete = True
            obj.save()
