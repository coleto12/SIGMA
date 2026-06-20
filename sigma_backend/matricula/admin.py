from django.contrib import admin
from .models import (
    PeriodoMatricula, RequisitoDocumental, SolicitudMatricula,
    SolicitudAsignatura, DocumentoAdjunto, MatriculaOficial,
)


@admin.register(PeriodoMatricula)
class PeriodoMatriculaAdmin(admin.ModelAdmin):
    list_display = ('id', 'periodo_academico', 'fecha_inicio', 'fecha_fin', 'estado', 'jefe_departamento')
    list_filter = ('estado', 'periodo_academico')


@admin.register(RequisitoDocumental)
class RequisitoDocumentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'formato', 'periodo_matricula')
    list_filter = ('formato', 'periodo_matricula')
    search_fields = ('nombre',)


class SolicitudAsignaturaInline(admin.TabularInline):
    model = SolicitudAsignatura
    extra = 1


class DocumentoAdjuntoInline(admin.TabularInline):
    model = DocumentoAdjunto
    extra = 0


@admin.register(SolicitudMatricula)
class SolicitudMatriculaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'periodo_matricula', 'num_intento', 'estado', 'created_at')
    list_filter = ('estado', 'periodo_matricula')
    search_fields = ('estudiante__codigo',)
    inlines = [SolicitudAsignaturaInline, DocumentoAdjuntoInline]


@admin.register(MatriculaOficial)
class MatriculaOficialAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud_matricula', 'fecha_emision', 'jefe_departamento')
    search_fields = ('solicitud_matricula__estudiante__codigo',)
