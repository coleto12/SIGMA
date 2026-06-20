"""
Serializers del bloque Notificaciones.
"""
from rest_framework import serializers
from .models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'tipo_evento', 'mensaje', 'leida', 'created_at', 'usuario']
        read_only_fields = ['tipo_evento', 'mensaje', 'created_at', 'usuario']
        # Nota: 'leida' es el único campo que el usuario final puede modificar
        # directamente (marcar como leída). El resto se genera automáticamente
        # desde notificaciones/services.py al ocurrir eventos del sistema.