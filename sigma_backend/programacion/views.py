"""
Views del bloque Programación Académica.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import ProgramacionAcademica, Salon, Grupo, HorarioGrupo
from .serializers import (
    ProgramacionAcademicaSerializer, SalonSerializer,
    GrupoSerializer, HorarioGrupoSerializer,
)
from usuarios.permissions import EsJefeDepartamentoOAdministrador


def _es_jefe_o_admin(request):
    rol = request.user.rol.nombre if request.user.rol else None
    return rol in ('Jefe de Departamento', 'Administrador')


# ---------------------------------------------------------------------------
# ProgramacionAcademica
#
# Regla de visibilidad (ver Modelo de Negocio - Gestión de Programación
# Académica del Periodo): un Estudiante solo puede ver programación con
# estado 'publicada'. El Jefe de Departamento/Administrador ven también
# las que están en construcción ('no_publicada').
# ---------------------------------------------------------------------------
class ProgramacionAcademicaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = ProgramacionAcademica.objects.select_related(
            'programa_academico', 'periodo_academico', 'jefe_departamento'
        ).all()

        if not _es_jefe_o_admin(request):
            items = items.filter(estado='publicada')

        periodo_id = request.query_params.get('periodo_academico')
        if periodo_id:
            items = items.filter(periodo_academico_id=periodo_id)

        serializer = ProgramacionAcademicaSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = ProgramacionAcademicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProgramacionAcademicaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(ProgramacionAcademica, pk=pk)
        if item.estado != 'publicada' and not _es_jefe_o_admin(request):
            return Response(
                {'detail': 'Esta programación académica aún no ha sido publicada.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ProgramacionAcademicaSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        item = get_object_or_404(ProgramacionAcademica, pk=pk)
        serializer = ProgramacionAcademicaSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        item = get_object_or_404(ProgramacionAcademica, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProgramacionAcademicaPublicarView(APIView):
    """
    POST /api/programacion/programaciones-academicas/<pk>/publicar/
    Acción explícita de publicación (caso de uso CU08 del Análisis Preliminar),
    separada del PUT genérico porque tiene significado de negocio propio.
    """
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    def post(self, request, pk):
        item = get_object_or_404(ProgramacionAcademica, pk=pk)
        if item.estado == 'publicada':
            return Response(
                {'detail': 'Esta programación académica ya está publicada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.estado = 'publicada'
        item.save(update_fields=['estado', 'updated_at'])
        serializer = ProgramacionAcademicaSerializer(item)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Salon
# ---------------------------------------------------------------------------
class SalonListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        salones = Salon.objects.select_related('campus').all()
        serializer = SalonSerializer(salones, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = SalonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalonDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        salon = get_object_or_404(Salon, pk=pk)
        serializer = SalonSerializer(salon)
        return Response(serializer.data)

    def put(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        salon = get_object_or_404(Salon, pk=pk)
        serializer = SalonSerializer(salon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        salon = get_object_or_404(Salon, pk=pk)
        salon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Grupo
# ---------------------------------------------------------------------------
class GrupoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        grupos = Grupo.objects.select_related(
            'asignatura', 'docente', 'programacion_academica'
        ).all()

        if not _es_jefe_o_admin(request):
            grupos = grupos.filter(programacion_academica__estado='publicada')

        programacion_id = request.query_params.get('programacion_academica')
        if programacion_id:
            grupos = grupos.filter(programacion_academica_id=programacion_id)

        asignatura_id = request.query_params.get('asignatura')
        if asignatura_id:
            grupos = grupos.filter(asignatura_id=asignatura_id)

        serializer = GrupoSerializer(grupos, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = GrupoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GrupoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        grupo = get_object_or_404(Grupo, pk=pk)
        if grupo.programacion_academica.estado != 'publicada' and not _es_jefe_o_admin(request):
            return Response(
                {'detail': 'Este grupo pertenece a una programación académica aún no publicada.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = GrupoSerializer(grupo)
        return Response(serializer.data)

    def put(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        grupo = get_object_or_404(Grupo, pk=pk)
        serializer = GrupoSerializer(grupo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        grupo = get_object_or_404(Grupo, pk=pk)
        grupo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# HorarioGrupo
# ---------------------------------------------------------------------------
class HorarioGrupoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        horarios = HorarioGrupo.objects.select_related('grupo', 'salon').all()
        grupo_id = request.query_params.get('grupo')
        if grupo_id:
            horarios = horarios.filter(grupo_id=grupo_id)
        serializer = HorarioGrupoSerializer(horarios, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = HorarioGrupoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HorarioGrupoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        horario = get_object_or_404(HorarioGrupo, pk=pk)
        serializer = HorarioGrupoSerializer(horario)
        return Response(serializer.data)

    def put(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        horario = get_object_or_404(HorarioGrupo, pk=pk)
        serializer = HorarioGrupoSerializer(horario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        horario = get_object_or_404(HorarioGrupo, pk=pk)
        horario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)