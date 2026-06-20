"""
Serializers del bloque Programación Académica.
"""
from rest_framework import serializers
from .models import ProgramacionAcademica, Salon, Grupo, HorarioGrupo


class ProgramacionAcademicaSerializer(serializers.ModelSerializer):
    programa_academico_nombre = serializers.CharField(source='programa_academico.nombre', read_only=True)
    periodo_academico_nombre = serializers.CharField(source='periodo_academico.nombre', read_only=True)

    class Meta:
        model = ProgramacionAcademica
        fields = [
            'id', 'estado', 'created_at', 'updated_at',
            'programa_academico', 'programa_academico_nombre',
            'periodo_academico', 'periodo_academico_nombre',
            'jefe_departamento',
        ]
        read_only_fields = ['created_at', 'updated_at']


class SalonSerializer(serializers.ModelSerializer):
    campus_nombre = serializers.CharField(source='campus.nombre', read_only=True)

    class Meta:
        model = Salon
        fields = ['id', 'nombre', 'capacidad', 'campus', 'campus_nombre']


class GrupoSerializer(serializers.ModelSerializer):
    asignatura_codigo = serializers.CharField(source='asignatura.codigo', read_only=True)
    asignatura_nombre = serializers.CharField(source='asignatura.nombre', read_only=True)
    docente_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Grupo
        fields = [
            'id', 'nombre', 'cupo_maximo', 'cupo_disponible',
            'programacion_academica', 'asignatura', 'asignatura_codigo', 'asignatura_nombre',
            'docente', 'docente_nombre',
        ]

    def get_docente_nombre(self, obj):
        return f'{obj.docente.primer_nombre} {obj.docente.primer_apellido}'

    def validate(self, attrs):
        cupo_maximo = attrs.get('cupo_maximo', getattr(self.instance, 'cupo_maximo', None))
        cupo_disponible = attrs.get('cupo_disponible', getattr(self.instance, 'cupo_disponible', None))
        if cupo_disponible is not None and cupo_maximo is not None and cupo_disponible > cupo_maximo:
            raise serializers.ValidationError(
                'El cupo disponible no puede ser mayor que el cupo máximo.'
            )
        return attrs


def _rangos_se_solapan(inicio_a, fin_a, inicio_b, fin_b):
    """True si [inicio_a, fin_a) se cruza con [inicio_b, fin_b)."""
    return inicio_a < fin_b and inicio_b < fin_a


class HorarioGrupoSerializer(serializers.ModelSerializer):
    grupo_repr = serializers.CharField(source='grupo.__str__', read_only=True)
    salon_nombre = serializers.CharField(source='salon.nombre', read_only=True)

    class Meta:
        model = HorarioGrupo
        fields = [
            'id', 'dia_semana', 'hora_inicio', 'hora_fin',
            'grupo', 'grupo_repr', 'salon', 'salon_nombre',
        ]

    def validate(self, attrs):
        dia_semana = attrs.get('dia_semana', getattr(self.instance, 'dia_semana', None))
        hora_inicio = attrs.get('hora_inicio', getattr(self.instance, 'hora_inicio', None))
        hora_fin = attrs.get('hora_fin', getattr(self.instance, 'hora_fin', None))
        grupo = attrs.get('grupo', getattr(self.instance, 'grupo', None))
        salon = attrs.get('salon', getattr(self.instance, 'salon', None))

        if hora_inicio is not None and hora_fin is not None and hora_inicio >= hora_fin:
            raise serializers.ValidationError(
                'La hora de inicio debe ser anterior a la hora de fin.'
            )

        # Candidatos del mismo día (excluyendo el propio registro si es una edición)
        candidatos = HorarioGrupo.objects.filter(dia_semana=dia_semana)
        if self.instance is not None:
            candidatos = candidatos.exclude(pk=self.instance.pk)

        for horario in candidatos.select_related('grupo', 'grupo__docente', 'salon'):
            se_solapan = _rangos_se_solapan(hora_inicio, hora_fin, horario.hora_inicio, horario.hora_fin)
            if not se_solapan:
                continue

            # Regla del negocio: unicidad de salón por horario.
            if horario.salon_id == salon.id:
                raise serializers.ValidationError(
                    f'El salón "{salon.nombre}" ya está ocupado el {dia_semana} '
                    f'de {horario.hora_inicio} a {horario.hora_fin}.'
                )

            # Regla del negocio: unicidad de docente por horario.
            if horario.grupo.docente_id == grupo.docente_id:
                raise serializers.ValidationError(
                    f'El docente ya tiene clase asignada el {dia_semana} '
                    f'de {horario.hora_inicio} a {horario.hora_fin} (grupo "{horario.grupo}").'
                )

        return attrs