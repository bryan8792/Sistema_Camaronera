from django.db import transaction
from .models import TipoCosto
from django.db import transaction
from app_empresa.app_reg_empresa.models import TipoCosto

@transaction.atomic
def cargar_tipos_costo_iniciales():
    """
    Carga los tipos de costo iniciales en la base de datos
    """
    # Lista de tipos de costo a crear
    tipos_costo = [
        # Costos de mano de obra
        {
            'nombre': 'Mano de Obra Directa',
            'descripcion': 'Sueldos y salarios del personal que trabaja directamente en la producción (alimentadores, cosechadores, etc.)'
        },
        {
            'nombre': 'Mano de Obra Indirecta',
            'descripcion': 'Sueldos y salarios de supervisores, personal técnico, etc.'
        },

        # Costos de insumos
        {
            'nombre': 'Alimento',
            'descripcion': 'Costos de alimento para camarón'
        },
        {
            'nombre': 'Fertilizantes',
            'descripcion': 'Fertilizantes para preparación de piscinas'
        },
        {
            'nombre': 'Probióticos',
            'descripcion': 'Probióticos y otros aditivos para el agua'
        },
        {
            'nombre': 'Larvas',
            'descripcion': 'Costo de adquisición de larvas'
        },

        # Costos de mantenimiento
        {
            'nombre': 'Mantenimiento de Piscinas',
            'descripcion': 'Reparaciones y mantenimiento de piscinas'
        },
        {
            'nombre': 'Mantenimiento de Equipos',
            'descripcion': 'Reparaciones y mantenimiento de bombas, aireadores, etc.'
        },

        # Costos de energía
        {
            'nombre': 'Electricidad',
            'descripcion': 'Consumo eléctrico para bombas, aireadores, etc.'
        },
        {
            'nombre': 'Combustible',
            'descripcion': 'Combustible para bombas, generadores, vehículos, etc.'
        },

        # Otros costos
        {
            'nombre': 'Análisis de Laboratorio',
            'descripcion': 'Análisis de calidad de agua, patologías, etc.'
        },
        {
            'nombre': 'Transporte',
            'descripcion': 'Transporte de insumos, personal, cosecha, etc.'
        },
        {
            'nombre': 'Depreciación',
            'descripcion': 'Depreciación de equipos e infraestructura'
        },
        {
            'nombre': 'Otros Costos',
            'descripcion': 'Otros costos operativos no categorizados'
        },
    ]

    # Crear los tipos de costo
    for tipo in tipos_costo:
        TipoCosto.objects.get_or_create(
            nombre=tipo['nombre'],
            defaults={'descripcion': tipo['descripcion']}
        )

    return len(tipos_costo)
