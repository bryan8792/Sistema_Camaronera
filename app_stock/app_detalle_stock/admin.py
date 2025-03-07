from django.contrib import admin

# Register your models here.
from Sistema_Camaronera.snippers import Attr
from app_inventario.app_categoria.models import *
from app_stock.app_detalle_stock.models import Producto_Stock


class Productos(admin.StackedInline):
    model = Producto
    extra = 0

@admin.register(Categoria)
class modelo(admin.ModelAdmin):
    list_display = Attr(Categoria)
    list_display_links = Attr(Categoria)
    inlines = [Productos]

@admin.register(Producto)
class modelo(admin.ModelAdmin):
    list_display = Attr(Producto)
    list_display_links = Attr(Producto)

@admin.register(Producto_Stock)
class modelo(admin.ModelAdmin):
    list_display = Attr(Producto_Stock)
    list_display_links = Attr(Producto_Stock)