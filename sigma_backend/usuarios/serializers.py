"""
Serializers del bloque Usuarios: autenticación (login) y CRUD de entidades.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Rol, Usuario, Estudiante, JefeDepartamento, Docente


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre']


class SigmaTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login institucional: se autentica con 'correo' (en vez de 'username',
    que es el campo por defecto de simplejwt) y el token incluye el rol
    del usuario, para que el frontend pueda decidir qué interfaz mostrar
    sin tener que hacer una segunda petición.
    """
    username_field = Usuario.USERNAME_FIELD  # 'correo'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['correo'] = user.correo
        token['rol'] = user.rol.nombre if user.rol else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['rol'] = self.user.rol.nombre if self.user.rol else None
        data['correo'] = self.user.correo
        data['usuario_id'] = self.user.id
        return data


class UsuarioSerializer(serializers.ModelSerializer):
    """Representación de Usuario para lectura (nunca expone el password)."""
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'correo', 'rol', 'rol_nombre', 'is_active']


class EstudianteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    correo = serializers.EmailField(source='usuario.correo', read_only=True)

    class Meta:
        model = Estudiante
        fields = [
            'id', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'nombre_completo', 'telefono', 'codigo', 'semestre_actual',
            'usuario', 'correo', 'programa_academico',
        ]


class JefeDepartamentoSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    correo = serializers.EmailField(source='usuario.correo', read_only=True)

    class Meta:
        model = JefeDepartamento
        fields = [
            'id', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'nombre_completo', 'codigo', 'usuario', 'correo', 'programa_academico',
        ]


class DocenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docente
        fields = [
            'id', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'codigo', 'correo', 'programa_academico',
        ]