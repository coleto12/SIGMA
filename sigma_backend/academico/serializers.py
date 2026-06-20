"""
Serializers del bloque Académico.
"""
from rest_framework import serializers
from .models import (
    PeriodoAcademico, PlanEstudio, Asignatura,
    PlanEstudioAsignatura, Prerrequisito, HistorialAcademico,
)


class PeriodoAcademicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoAcademico
        fields = ['id', 'nombre', 'fecha_inicio', 'fecha_fin', 'estado']


class PlanEstudioSerializer(serializers.ModelSerializer):
    programa_academico_nombre = serializers.CharField(source='programa_academico.nombre', read_only=True)

    class Meta:
        model = PlanEstudio
        fields = [
            'id', 'nombre', 'version', 'estado',
            'created_at', 'updated_at',
            'programa_academico', 'programa_academico_nombre',
        ]
        read_only_fields = ['created_at', 'updated_at']


class AsignaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asignatura
        fields = ['id', 'nombre', 'codigo']


class PlanEstudioAsignaturaSerializer(serializers.ModelSerializer):
    asignatura_codigo = serializers.CharField(source='asignatura.codigo', read_only=True)
    asignatura_nombre = serializers.CharField(source='asignatura.nombre', read_only=True)
    plan_estudio_nombre = serializers.CharField(source='plan_estudio.nombre', read_only=True)

    class Meta:
        model = PlanEstudioAsignatura
        fields = [
            'id', 'plan_estudio', 'plan_estudio_nombre',
            'asignatura', 'asignatura_codigo', 'asignatura_nombre',
            'creditos', 'semestre',
        ]


class PrerrequisitoSerializer(serializers.ModelSerializer):
    asignatura_codigo = serializers.CharField(source='asignatura.codigo', read_only=True)
    asignatura_prerrequisito_codigo = serializers.CharField(source='asignatura_prerrequisito.codigo', read_only=True)

    class Meta:
        model = Prerrequisito
        fields = [
            'id', 'asignatura', 'asignatura_codigo',
            'asignatura_prerrequisito', 'asignatura_prerrequisito_codigo',
        ]

    def validate(self, attrs):
        # Una asignatura no puede ser prerrequisito de sí misma.
        if attrs['asignatura'] == attrs['asignatura_prerrequisito']:
            raise serializers.ValidationError(
                'Una asignatura no puede ser prerrequisito de sí misma.'
            )
        return attrs


class HistorialAcademicoSerializer(serializers.ModelSerializer):
    estudiante_codigo = serializers.CharField(source='estudiante.codigo', read_only=True)
    asignatura_codigo = serializers.CharField(source='asignatura.codigo', read_only=True)
    asignatura_nombre = serializers.CharField(source='asignatura.nombre', read_only=True)
    periodo_academico_nombre = serializers.CharField(source='periodo_academico.nombre', read_only=True)

    class Meta:
        model = HistorialAcademico
        fields = [
            'id', 'nota', 'estado', 'created_at',
            'estudiante', 'estudiante_codigo',
            'asignatura', 'asignatura_codigo', 'asignatura_nombre',
            'periodo_academico', 'periodo_academico_nombre',
        ]
        read_only_fields = ['created_at']