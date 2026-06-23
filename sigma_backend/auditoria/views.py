"""
Vista de solo lectura para consultar el log de auditoría (CU09).
Solo Jefe de Departamento o Administrador pueden verlo.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import RegistroAuditoria
from .serializers import RegistroAuditoriaSerializer
from usuarios.permissions import EsJefeDepartamentoOAdministrador


class RegistroAuditoriaListView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    def get(self, request):
        items = RegistroAuditoria.objects.select_related('usuario').all()

        modelo = request.query_params.get('modelo_afectado')
        if modelo:
            items = items.filter(modelo_afectado=modelo)

        objeto_id = request.query_params.get('objeto_id')
        if objeto_id:
            items = items.filter(objeto_id=objeto_id)

        # Límite simple para no devolver miles de filas de golpe; quien
        # necesite paginación real puede pedirla como mejora futura.
        items = items[:200]

        serializer = RegistroAuditoriaSerializer(items, many=True)
        return Response(serializer.data)