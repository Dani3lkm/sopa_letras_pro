from django.contrib import admin
from .models import Nivel, Desafio

@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    # Mostramos el ID para que sepas qué número poner en el desafío
    list_display = ('id', 'numero', 'titulo', 'dimension')

@admin.register(Desafio)
class DesafioAdmin(admin.ModelAdmin):
    list_display = ('palabra', 'nivel')
