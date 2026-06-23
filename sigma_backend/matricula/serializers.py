"""
Serializers del bloque Matrícula Académica.

Contiene la lógica de validación más importante del sistema:
- SolicitudAsignaturaSerializer valida, al agregar cada asignatura:
  1) que la asignatura no esté ya aprobada en el historial del estudiante
     (ver Modelo de Negocio 4.3.2 - Elegibilidad de matrícula basada en
     historia: no se puede volver a cursar lo ya aprobado),
  2) que el periodo de matrícula esté publicado y dentro de fechas,
  3) que el estudiante cumpla los prerrequisitos académicos de la
     asignatura (contra HistorialAcademico, estado 'aprobada'),
  4) que el horario del grupo no se cruce con otro grupo ya presente
     en la MISMA solicitud de matrícula.

El control de cupo disponible NO se valida aquí (se decidió que el cupo
solo se descuenta al momento de la aprobación por el Jefe de Departamento,
ver matricula/views.py - SolicitudMatriculaAprobarView).
"""
from rest_framework import serializers
from django.utils import timezone

from .models import (
    PeriodoMatricula, RequisitoDocumental, SolicitudMatricula,
    SolicitudAsignatura, DocumentoAdjunto, MatriculaOficial,
)
from academico.models import Prerrequisito, HistorialAcademico
from programacion.models import HorarioGrupo


class PeriodoMatriculaSerializer(serializers.ModelSerializer):
    periodo_academico_nombre = serializers.CharField(source='periodo_academico.nombre', read_only=True)

    class Meta:
        model = PeriodoMatricula
        fields = [
            'id', 'fecha_inicio', 'fecha_fin', 'estado',
            'created_at', 'updated_at',
            'periodo_academico', 'periodo_academico_nombre',
            'jefe_departamento',
        ]
        read_only_fields = ['created_at', 'updated_at']


class RequisitoDocumentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequisitoDocumental
        fields = ['id', 'nombre', 'descripcion', 'formato', 'periodo_matricula']


class SolicitudMatriculaSerializer(serializers.ModelSerializer):
    estudiante_codigo = serializers.CharField(source='estudiante.codigo', read_only=True)
    estudiante_nombre = serializers.CharField(source='estudiante.nombre_completo', read_only=True)
    periodo_matricula_nombre = serializers.CharField(source='periodo_matricula.periodo_academico.nombre', read_only=True)

    class Meta:
        model = SolicitudMatricula
        fields = [
            'id', 'num_intento', 'estado', 'motivo_rechazo', 'enviada_formalmente',
            'created_at', 'updated_at',
            'estudiante', 'estudiante_codigo', 'estudiante_nombre',
            'periodo_matricula', 'periodo_matricula_nombre',
        ]
        read_only_fields = ['num_intento', 'estado', 'motivo_rechazo', 'enviada_formalmente', 'created_at', 'updated_at']

    def validate_periodo_matricula(self, periodo_matricula):
        if periodo_matricula.estado != 'publicado':
            raise serializers.ValidationError(
                'El periodo de matrícula no está publicado todavía.'
            )
        hoy = timezone.localdate()
        if not (periodo_matricula.fecha_inicio <= hoy <= periodo_matricula.fecha_fin):
            raise serializers.ValidationError(
                'La fecha actual está fuera del rango del periodo de matrícula '
                f'({periodo_matricula.fecha_inicio} a {periodo_matricula.fecha_fin}).'
            )
        return periodo_matricula

    def create(self, validated_data):
        # num_intento = cantidad de solicitudes previas del estudiante en este
        # periodo + 1 (ver decisión de diseño: resubmisión crea nuevo registro).
        intentos_previos = SolicitudMatricula.objects.filter(
            estudiante=validated_data['estudiante'],
            periodo_matricula=validated_data['periodo_matricula'],
        ).count()
        validated_data['num_intento'] = intentos_previos + 1
        validated_data['estado'] = 'pendiente_revision'
        return super().create(validated_data)


def _rangos_se_solapan(inicio_a, fin_a, inicio_b, fin_b):
    return inicio_a < fin_b and inicio_b < fin_a


class SolicitudAsignaturaSerializer(serializers.ModelSerializer):
    asignatura_codigo = serializers.CharField(source='grupo.asignatura.codigo', read_only=True)
    asignatura_nombre = serializers.CharField(source='grupo.asignatura.nombre', read_only=True)
    grupo_nombre = serializers.CharField(source='grupo.nombre', read_only=True)

    class Meta:
        model = SolicitudAsignatura
        fields = [
            'id', 'solicitud_matricula', 'grupo',
            'asignatura_codigo', 'asignatura_nombre', 'grupo_nombre',
        ]

    def validate(self, attrs):
        solicitud = attrs['solicitud_matricula']
        grupo = attrs['grupo']

        if solicitud.estado != 'pendiente_revision':
            raise serializers.ValidationError(
                'Solo se pueden agregar asignaturas a una solicitud pendiente de revisión.'
            )

        if solicitud.enviada_formalmente:
            raise serializers.ValidationError(
                'Esta solicitud ya fue enviada formalmente y no puede modificarse. '
                'Espera la revisión del Jefe de Departamento.'
            )

        asignatura = grupo.asignatura
        estudiante = solicitud.estudiante

        # --- 0) Elegibilidad por historial (ver Modelo de Negocio 4.3.2):
        # un estudiante no puede volver a matricular una asignatura que ya
        # tiene aprobada en su historial académico. Sí puede reintentarla
        # si la reprobó, o si nunca la ha cursado.
        ya_aprobada = HistorialAcademico.objects.filter(
            estudiante=estudiante,
            asignatura=asignatura,
            estado='aprobada',
        ).exists()
        if ya_aprobada:
            raise serializers.ValidationError(
                f'Ya aprobaste la asignatura "{asignatura.codigo} - {asignatura.nombre}" '
                'en un periodo anterior; no puedes volver a matricularla.'
            )

        # --- 1) Validación de prerrequisitos (contra HistorialAcademico) ---
        prerrequisitos = Prerrequisito.objects.filter(asignatura=asignatura)
        for prereq in prerrequisitos:
            aprobado = HistorialAcademico.objects.filter(
                estudiante=estudiante,
                asignatura=prereq.asignatura_prerrequisito,
                estado='aprobada',
            ).exists()
            if not aprobado:
                raise serializers.ValidationError(
                    f'No cumples el prerrequisito "{prereq.asignatura_prerrequisito.codigo} - '
                    f'{prereq.asignatura_prerrequisito.nombre}" para matricular '
                    f'"{asignatura.codigo} - {asignatura.nombre}".'
                )

        # --- 2) Validación de cruce de horario dentro de la MISMA solicitud ---
        horarios_nuevo_grupo = HorarioGrupo.objects.filter(grupo=grupo)
        otras_asignaturas = SolicitudAsignatura.objects.filter(
            solicitud_matricula=solicitud
        ).exclude(grupo=grupo).select_related('grupo')

        for otra in otras_asignaturas:
            horarios_existentes = HorarioGrupo.objects.filter(grupo=otra.grupo)
            for h_nuevo in horarios_nuevo_grupo:
                for h_existente in horarios_existentes:
                    if h_nuevo.dia_semana != h_existente.dia_semana:
                        continue
                    if _rangos_se_solapan(
                        h_nuevo.hora_inicio, h_nuevo.hora_fin,
                        h_existente.hora_inicio, h_existente.hora_fin,
                    ):
                        raise serializers.ValidationError(
                            f'El horario de "{asignatura.codigo}" (grupo {grupo.nombre}) se '
                            f'cruza con "{otra.grupo.asignatura.codigo}" (grupo {otra.grupo.nombre}) '
                            f'el {h_nuevo.dia_semana}.'
                        )

        # --- 3) Límite máximo de créditos por solicitud de matrícula ---
        # No está exigido explícitamente por el Modelo de Negocio, pero es
        # una regla razonable de carga académica por periodo (referencia:
        # ~4 asignaturas de 2-4 créditos cada una, equivalentes a un
        # semestre normal del plan de estudios).
        MAXIMO_CREDITOS_POR_SOLICITUD = 12

        def _creditos_en_plan_del_estudiante(asig):
            fila_plan = asig.planes_asignatura.filter(
                plan_estudio__programa_academico=estudiante.programa_academico,
                plan_estudio__estado='vigente',
            ).first()
            return fila_plan.creditos if fila_plan else 0

        creditos_actuales = sum(
            _creditos_en_plan_del_estudiante(otra.grupo.asignatura) for otra in otras_asignaturas
        )
        creditos_nueva = _creditos_en_plan_del_estudiante(asignatura)

        if creditos_actuales + creditos_nueva > MAXIMO_CREDITOS_POR_SOLICITUD:
            raise serializers.ValidationError(
                f'No puedes matricular "{asignatura.codigo} - {asignatura.nombre}" '
                f'({creditos_nueva} créditos): superarías el máximo de '
                f'{MAXIMO_CREDITOS_POR_SOLICITUD} créditos por solicitud '
                f'(llevas {creditos_actuales} créditos seleccionados).'
            )

        return attrs


class DocumentoAdjuntoSerializer(serializers.ModelSerializer):
    requisito_nombre = serializers.CharField(source='requisito_documental.nombre', read_only=True)

    class Meta:
        model = DocumentoAdjunto
        fields = [
            'id', 'nombre_archivo', 'archivo', 'created_at', 'version',
            'solicitud_matricula', 'requisito_documental', 'requisito_nombre',
        ]
        read_only_fields = ['created_at', 'version']

    def create(self, validated_data):
        solicitud = validated_data['solicitud_matricula']
        if solicitud.enviada_formalmente:
            raise serializers.ValidationError(
                'Esta solicitud ya fue enviada formalmente; no puedes modificar sus documentos.'
            )
        # Si ya existe un documento para el mismo requisito en la misma
        # solicitud, este nuevo se guarda con version incrementada (no
        # se sobrescribe el anterior, queda como historial).
        existentes = DocumentoAdjunto.objects.filter(
            solicitud_matricula=validated_data['solicitud_matricula'],
            requisito_documental=validated_data['requisito_documental'],
        ).order_by('-version').first()
        validated_data['version'] = (existentes.version + 1) if existentes else 1
        return super().create(validated_data)


class MatriculaOficialSerializer(serializers.ModelSerializer):
    estudiante_codigo = serializers.CharField(source='solicitud_matricula.estudiante.codigo', read_only=True)
    estudiante_nombre = serializers.CharField(source='solicitud_matricula.estudiante.nombre_completo', read_only=True)
    periodo_academico_nombre = serializers.CharField(
        source='solicitud_matricula.periodo_matricula.periodo_academico.nombre', read_only=True
    )

    class Meta:
        model = MatriculaOficial
        fields = [
            'id', 'documento', 'fecha_emision',
            'solicitud_matricula', 'estudiante_codigo', 'estudiante_nombre',
            'periodo_academico_nombre', 'jefe_departamento',
        ]
        read_only_fields = ['documento', 'fecha_emision']