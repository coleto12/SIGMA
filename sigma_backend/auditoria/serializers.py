from rest_framework import serializers
from .models import RegistroAuditoria


class RegistroAuditoriaSerializer(serializers.ModelSerializer):
    usuario_correo = serializers.CharField(source='usuario.correo', read_only=True, default=None)

    class Meta:
        model = RegistroAuditoria
        fields = [
            'id', 'fecha_hora', 'usuario', 'usuario_correo',
            'accion', 'modelo_afectado', 'objeto_id', 'descripcion',
        ]