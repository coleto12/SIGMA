"""
Serializers del bloque Institucional.
Cada serializer valida y convierte a/desde JSON una entidad del bloque.
"""
from rest_framework import serializers
from .models import Campus, Facultad, NivelFormacion, ProgramaAcademico


class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = ['id', 'nombre', 'direccion']


class FacultadSerializer(serializers.ModelSerializer):
    # Solo lectura: nombre legible del campus, además del id editable.
    campus_nombre = serializers.CharField(source='campus.nombre', read_only=True)

    class Meta:
        model = Facultad
        fields = ['id', 'nombre', 'campus', 'campus_nombre']


class NivelFormacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NivelFormacion
        fields = ['id', 'nombre']


class ProgramaAcademicoSerializer(serializers.ModelSerializer):
    facultad_nombre = serializers.CharField(source='facultad.nombre', read_only=True)
    nivel_formacion_nombre = serializers.CharField(source='nivel_formacion.nombre', read_only=True)

    class Meta:
        model = ProgramaAcademico
        fields = [
            'id', 'nombre', 'codigo',
            'facultad', 'facultad_nombre',
            'nivel_formacion', 'nivel_formacion_nombre',
        ]