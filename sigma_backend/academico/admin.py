from django.contrib import admin
from .models import (
    PeriodoAcademico, PlanEstudio, Asignatura,
    PlanEstudioAsignatura, Prerrequisito, HistorialAcademico,
)


@admin.register(PeriodoAcademico)
class PeriodoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'fecha_inicio', 'fecha_fin', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre',)


class PlanEstudioAsignaturaInline(admin.TabularInline):
    model = PlanEstudioAsignatura
    extra = 1


@admin.register(PlanEstudio)
class PlanEstudioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'version', 'estado', 'programa_academico')
    list_filter = ('estado', 'programa_academico')
    search_fields = ('nombre', 'version')
    inlines = [PlanEstudioAsignaturaInline]


@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(Prerrequisito)
class PrerrequisitoAdmin(admin.ModelAdmin):
    list_display = ('id', 'asignatura', 'asignatura_prerrequisito')
    search_fields = ('asignatura__codigo', 'asignatura_prerrequisito__codigo')


@admin.register(HistorialAcademico)
class HistorialAcademicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'asignatura', 'periodo_academico', 'estado', 'nota')
    list_filter = ('estado', 'periodo_academico')
    search_fields = ('estudiante__codigo', 'asignatura__codigo')
