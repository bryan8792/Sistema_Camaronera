from django.core.management.base import BaseCommand
from app_empresa.app_reg_empresa.initial_data import cargar_tipos_costo_iniciales  # Ajusta esta importación

class Command(BaseCommand):
    help = 'Carga los tipos de costo iniciales en la base de datos'

    def handle(self, *args, **options):
        try:
            num_tipos = cargar_tipos_costo_iniciales()
            self.stdout.write(self.style.SUCCESS(f'Se han cargado {num_tipos} tipos de costo correctamente.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al cargar tipos de costo: {str(e)}'))