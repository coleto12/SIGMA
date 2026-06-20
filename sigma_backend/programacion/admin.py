from django.contrib import admin
from .models import ProgramacionAcademica, Salon, Grupo, HorarioGrupo


class HorarioGrupoInline(admin.TabularInline):
    model = HorarioGrupo
    extra = 1


@admin.register(ProgramacionAcademica)
class ProgramacionAcademicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'programa_academico', 'periodo_academico', 'estado', 'jefe_departamento')
    list_filter = ('estado', 'periodo_academico')
    search_fields = ('programa_academico__nombre',)


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'capacidad', 'campus')
    list_filter = ('campus',)
    search_fields = ('nombre',)


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'asignatura', 'docente', 'cupo_maximo', 'cupo_disponible', 'programacion_academica')
    list_filter = ('programacion_academica', 'asignatura')
    search_fields = ('nombre', 'asignatura__codigo')
    inlines = [HorarioGrupoInline]


@admin.register(HorarioGrupo)
class HorarioGrupoAdmin(admin.ModelAdmin):
    list_display = ('id', 'grupo', 'dia_semana', 'hora_inicio', 'hora_fin', 'salon')
    list_filter = ('dia_semana', 'salon')
