from django.contrib import admin
from .models import Campus, Facultad, NivelFormacion, ProgramaAcademico


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion')
    search_fields = ('nombre',)


@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'campus')
    list_filter = ('campus',)
    search_fields = ('nombre',)


@admin.register(NivelFormacion)
class NivelFormacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(ProgramaAcademico)
class ProgramaAcademicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre', 'facultad', 'nivel_formacion')
    list_filter = ('facultad', 'nivel_formacion')
    search_fields = ('nombre', 'codigo')
