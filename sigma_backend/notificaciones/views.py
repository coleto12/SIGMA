"""
Views del bloque Notificaciones.

Regla de visibilidad: cada usuario ve únicamente SUS PROPIAS notificaciones,
sin excepción de rol (a diferencia de otros bloques, aquí ni el Jefe de
Departamento ni el Administrador pueden ver notificaciones de otro usuario,
por tratarse de mensajería personal).
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Notificacion
from .serializers import NotificacionSerializer


class NotificacionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Notificacion.objects.filter(usuario=request.user)

        leida = request.query_params.get('leida')
        if leida is not None:
            items = items.filter(leida=leida.lower() == 'true')

        serializer = NotificacionSerializer(items, many=True)
        return Response(serializer.data)


class NotificacionDetailView(APIView):
    """
    GET: ver una notificación propia.
    PATCH/PUT: marcarla como leída (es la única edición permitida).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
        serializer = NotificacionSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        item = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
        leida = request.data.get('leida')
        if leida is None:
            return Response(
                {'detail': 'Solo se permite actualizar el campo "leida".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.leida = bool(leida)
        item.save(update_fields=['leida'])
        serializer = NotificacionSerializer(item)
        return Response(serializer.data)

    def delete(self, request, pk):
        item = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificacionMarcarTodasLeidasView(APIView):
    """POST /api/notificaciones/marcar-todas-leidas/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        actualizadas = Notificacion.objects.filter(
            usuario=request.user, leida=False
        ).update(leida=True)
        return Response({'notificaciones_actualizadas': actualizadas})