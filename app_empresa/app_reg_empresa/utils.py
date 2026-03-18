from django.contrib.auth import get_user_model
from django_tenants.utils import get_tenant_model, schema_context
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group, Permission
from app_user.models import TipoModulo, Modulo, GrupoModulo
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType


User = get_user_model()


# ==========================================================
# 1) CREA EMPRESA Y USUARIO ADMIN EN EL TENANT
# ==========================================================
def clonar_empresa_en_tenant(empresa, schema):

    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group
    from django_tenants.utils import schema_context

    User = get_user_model()

    with schema_context(schema):
        from django.db import connection
        print("CLONANDO EMPRESA EN:", connection.schema_name)

        from app_empresa.app_reg_empresa.models import Empresa

        # eliminar duplicados si existen
        if Empresa.objects.filter(ruc=empresa.ruc).exists():
            return

        empresa_tenant = Empresa.objects.create(
            nombre=empresa.nombre,
            ruc=empresa.ruc,
            business_name=empresa.business_name,
            tradename=empresa.tradename,
            direccion=empresa.direccion,
            main_address=empresa.main_address,
            establishment_address=empresa.establishment_address,
            siglas=empresa.siglas,
            establishment_code=empresa.establishment_code,
            scheme=empresa.scheme,
            schema_name=empresa.schema_name,
            aperturada=empresa.aperturada,
            actividad=empresa.actividad,
            logo=empresa.logo,
            obligated_accounting=empresa.obligated_accounting,
            environment_type=empresa.environment_type,
            emission_type=empresa.emission_type,
            retention_agent=empresa.retention_agent,
            mobile=empresa.mobile,
            phone=empresa.phone,
            email=empresa.email,
            website=empresa.website,
            iva=empresa.iva,
            vat_percentage=empresa.vat_percentage,
            electronic_signature_key=empresa.electronic_signature_key,
            electronic_signature=empresa.electronic_signature,
            email_host=empresa.email_host,
            email_port=empresa.email_port,
            email_host_user=empresa.email_host_user,
            email_host_password=empresa.email_host_password,
            estado=empresa.estado,
            issuing_point_code=empresa.issuing_point_code,
            special_taxpayer=empresa.special_taxpayer,
            description=empresa.description,
        )

        user, created = User.objects.get_or_create(
            username=empresa.ruc,
            defaults={
                "names": empresa.nombre,
                "email": getattr(empresa, "email", None),
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            }
        )

        user.set_password(empresa.ruc)
        user.save()

        group, _ = Group.objects.get_or_create(name="ADMIN")
        user.groups.add(group)


# ==========================================================
# 2) CLONA CONFIGURACIÓN BASE DESDE PUBLIC
# ==========================================================
def clonar_datos_base_en_tenant(schema):

    schema = schema

    # ===============================
    # LEER DATOS DESDE PUBLIC
    # ===============================
    with schema_context("public"):

        grupos_data = list(
            Group.objects.values("name")
        )

        modulos_data = list(
            Modulo.objects.values(
                "nombre",
                "url",
                "activo"
            )
        )

        grupos_modulos_data = list(
            GrupoModulo.objects.select_related("grupo", "modulo")
            .values(
                "grupo__name",
                "modulo__nombre",
                "can_add",
                "can_change",
                "can_delete",
                "can_view",
            )
        )

    # ===============================
    # CREAR EN TENANT
    # ===============================
    with schema_context(schema):

        # Crear grupos
        for g in grupos_data:
            Group.objects.get_or_create(name=g["name"])

        # Crear módulos
        for m in modulos_data:
            Modulo.objects.get_or_create(
                nombre=m["nombre"],
                defaults={
                    "url": m["url"],
                    "activo": m["activo"],
                }
            )

        # Crear relación GrupoModulo
        for gm in grupos_modulos_data:

            grupo = Group.objects.filter(
                name=gm["grupo__name"]
            ).first()

            modulo = Modulo.objects.filter(
                nombre=gm["modulo__nombre"]
            ).first()

            if not grupo or not modulo:
                continue

            GrupoModulo.objects.get_or_create(
                grupo=grupo,
                modulo=modulo,
                defaults={
                    "can_add": gm["can_add"],
                    "can_change": gm["can_change"],
                    "can_delete": gm["can_delete"],
                    "can_view": gm["can_view"],
                }
            )


# ==========================================================
# RESET CLAVE DESDE SUPERADMIN
# ==========================================================
def reset_password_empresa(request, schema, username):

    with schema_context(schema):
        user = User.objects.filter(username=username).first()

        if not user:
            messages.error(request, "Usuario no encontrado")
            return redirect('app_empresa:superadmin_usuarios')

        if request.method == "POST":
            nueva = request.POST.get("password")

            user.set_password(nueva)
            user.is_active = True
            user.save()

            messages.success(request, "Clave actualizada correctamente")
            return redirect('app_empresa:superadmin_usuarios')

    return render(request, "superadmin/reset_password.html", {
        "schema": schema,
        "username": username
    })


# ==========================================================
# LISTADO SUPERADMIN DE USUARIOS POR TENANT
# ==========================================================
def superadmin_usuarios(request):
    Tenant = get_tenant_model()

    data = []

    for tenant in Tenant.objects.exclude(schema_name='public'):
        with schema_context(tenant.schema_name):
            for u in User.objects.all():
                data.append({
                    'schema': tenant.schema_name,
                    'empresa': tenant.name,
                    'username': u.username,
                    'activo': u.is_active,
                })

    return render(request, 'superadmin/usuarios.html', {'usuarios': data})
