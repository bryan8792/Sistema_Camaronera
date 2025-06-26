#!/usr/bin/env python
"""
Script para limpiar y recrear las migraciones de la base de datos
"""
import os
import sys
import django
from pathlib import Path

# Obtener la ruta del directorio del proyecto (donde está manage.py)
current_dir = Path(__file__).parent
project_root = current_dir.parent

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Cambiar al directorio del proyecto
os.chdir(project_root)

django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType


def reset_migrations():
    """Resetear las migraciones de app_user"""
    print("🔄 Reseteando migraciones...")

    try:
        # Eliminar archivos de migración existentes (excepto __init__.py)
        migrations_dir = project_root / 'app_user' / 'migrations'

        if migrations_dir.exists():
            for file in migrations_dir.glob('*.py'):
                if file.name != '__init__.py':
                    file.unlink()
                    print(f"   ✅ Eliminado: {file.name}")

        # Crear nuevas migraciones
        print("📝 Creando nuevas migraciones...")
        execute_from_command_line(['manage.py', 'makemigrations', 'app_user'])

        print("✅ Migraciones recreadas exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error al resetear migraciones: {e}")
        return False


def apply_migrations():
    """Aplicar las migraciones"""
    print("🚀 Aplicando migraciones...")

    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migraciones aplicadas exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error al aplicar migraciones: {e}")
        return False


def create_superuser():
    """Crear un superusuario si no existe"""
    print("👤 Verificando superusuario...")

    try:
        from app_user.models import User

        if not User.objects.filter(is_superuser=True).exists():
            print("📝 Creando superusuario...")
            User.objects.create_superuser(
                username='admin',
                email='admin@admin.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            print("✅ Superusuario creado: admin/admin123")
        else:
            print("✅ Ya existe un superusuario")

        return True

    except Exception as e:
        print(f"❌ Error al crear superusuario: {e}")
        return False


def create_sample_data():
    """Crear datos de ejemplo"""
    print("📊 Creando datos de ejemplo...")

    try:
        from app_user.models import TipoModulo, Modulo

        # Crear tipos de módulo
        tipos = [
            {'nombre': 'Sistema', 'descripcion': 'Módulos del sistema principal'},
            {'nombre': 'Reportes', 'descripcion': 'Módulos de reportes y estadísticas'},
            {'nombre': 'Configuración', 'descripcion': 'Módulos de configuración'},
        ]

        for tipo_data in tipos:
            tipo, created = TipoModulo.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults={'descripcion': tipo_data['descripcion']}
            )
            if created:
                print(f"   ✅ Tipo de módulo creado: {tipo.nombre}")

        # Crear módulos de ejemplo
        tipo_sistema = TipoModulo.objects.get(nombre='Sistema')
        tipo_reportes = TipoModulo.objects.get(nombre='Reportes')

        modulos = [
            {'nombre': 'Usuarios', 'tipo': tipo_sistema, 'url': '/usuarios/', 'icono': 'fas fa-users'},
            {'nombre': 'Grupos', 'tipo': tipo_sistema, 'url': '/grupos/', 'icono': 'fas fa-user-friends'},
            {'nombre': 'Permisos', 'tipo': tipo_sistema, 'url': '/permisos/', 'icono': 'fas fa-shield-alt'},
            {'nombre': 'Reporte de Usuarios', 'tipo': tipo_reportes, 'url': '/reportes/usuarios/',
             'icono': 'fas fa-chart-bar'},
        ]

        for modulo_data in modulos:
            modulo, created = Modulo.objects.get_or_create(
                nombre=modulo_data['nombre'],
                defaults={
                    'tipo': modulo_data['tipo'],
                    'url': modulo_data['url'],
                    'icono': modulo_data['icono']
                }
            )
            if created:
                print(f"   ✅ Módulo creado: {modulo.nombre}")

        print("✅ Datos de ejemplo creados")
        return True

    except Exception as e:
        print(f"❌ Error al crear datos de ejemplo: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Iniciando reparación de base de datos...")
    print("=" * 50)
    print(f"📁 Directorio del proyecto: {project_root}")
    print(f"🐍 Python path: {sys.path[0]}")
    print("=" * 50)

    # Paso 1: Resetear migraciones
    if not reset_migrations():
        return False

    print("\n" + "=" * 50)

    # Paso 2: Aplicar migraciones
    if not apply_migrations():
        return False

    print("\n" + "=" * 50)

    # Paso 3: Crear superusuario
    if not create_superuser():
        return False

    print("\n" + "=" * 50)

    # Paso 4: Crear datos de ejemplo
    if not create_sample_data():
        return False

    print("\n" + "=" * 50)
    print("🎉 ¡Reparación completada exitosamente!")
    print("\nPuedes iniciar sesión con:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\n" + "=" * 50)

    return True


if __name__ == '__main__':
    main()
