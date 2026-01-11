from django.apps import AppConfig


class AppDetalleStockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_stock.app_detalle_stock'

    def ready(self):
        import app_stock.app_detalle_stock.signals

