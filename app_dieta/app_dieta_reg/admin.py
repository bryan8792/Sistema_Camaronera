from django.contrib import admin

# Register your models here.
from Sistema_Camaronera.snippers import Attr
from app_dieta.app_dieta_reg.models import *

class Mes(admin.StackedInline):
    model = MesDieta
    extra = 0

@admin.register(AnioDieta)
class modelo(admin.ModelAdmin):
    list_display = Attr(AnioDieta)
    list_display_links = Attr(AnioDieta)
    inlines = [Mes]

class Dia(admin.StackedInline):
    model = DiaDietaRegistro
    extra = 0

@admin.register(MesDieta)
class modelo(admin.ModelAdmin):
    list_display = Attr(MesDieta)
    list_display_links = Attr(MesDieta)
    inlines = [Dia]

@admin.register(DiaDietaRegistro)
class modelo(admin.ModelAdmin):
    list_display = Attr(DiaDietaRegistro)
    list_display_links = Attr(DiaDietaRegistro)


@admin.register(DetalleDiaDieta)
class modelo(admin.ModelAdmin):
    list_display = Attr(DetalleDiaDieta)
    list_display_links = Attr(DetalleDiaDieta)