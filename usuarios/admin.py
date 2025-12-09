from django.contrib import admin
from .models import Pacientes

@admin.register(Pacientes)
class PacientesAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "telefone", "ativo")
    search_fields = ("nome", "telefone")
    list_filter = ("ativo",)
