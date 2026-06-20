"""
Views del bloque Académico.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import (
    PeriodoAcademico, PlanEstudio, Asignatura,
    PlanEstudioAsignatura, Prerrequisito, HistorialAcademico,
)
from .serializers import (
    PeriodoAcademicoSerializer, PlanEstudioSerializer, AsignaturaSerializer,
    PlanEstudioAsignaturaSerializer, PrerrequisitoSerializer, HistorialAcademicoSerializer,
)
from usuarios.permissions import EsJefeDepartamentoOAdministrador


# ---------------------------------------------------------------------------
# PeriodoAcademico
# ---------------------------------------------------------------------------
class PeriodoAcademicoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        periodos = PeriodoAcademico.objects.all()
        serializer = PeriodoAcademicoSerializer(periodos, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.check_object_permissions(request, None)
        serializer = PeriodoAcademicoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PeriodoAcademicoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        periodo = get_object_or_404(PeriodoAcademico, pk=pk)
        serializer = PeriodoAcademicoSerializer(periodo)
        return Response(serializer.data)

    def put(self, request, pk):
        periodo = get_object_or_404(PeriodoAcademico, pk=pk)
        serializer = PeriodoAcademicoSerializer(periodo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        periodo = get_object_or_404(PeriodoAcademico, pk=pk)
        periodo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# PlanEstudio
# ---------------------------------------------------------------------------
class PlanEstudioListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        planes = PlanEstudio.objects.select_related('programa_academico').all()
        serializer = PlanEstudioSerializer(planes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PlanEstudioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlanEstudioDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        plan = get_object_or_404(PlanEstudio, pk=pk)
        serializer = PlanEstudioSerializer(plan)
        return Response(serializer.data)

    def put(self, request, pk):
        plan = get_object_or_404(PlanEstudio, pk=pk)
        serializer = PlanEstudioSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        plan = get_object_or_404(PlanEstudio, pk=pk)
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Asignatura
# ---------------------------------------------------------------------------
class AsignaturaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        asignaturas = Asignatura.objects.all()
        serializer = AsignaturaSerializer(asignaturas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AsignaturaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AsignaturaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        asignatura = get_object_or_404(Asignatura, pk=pk)
        serializer = AsignaturaSerializer(asignatura)
        return Response(serializer.data)

    def put(self, request, pk):
        asignatura = get_object_or_404(Asignatura, pk=pk)
        serializer = AsignaturaSerializer(asignatura, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        asignatura = get_object_or_404(Asignatura, pk=pk)
        asignatura.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# PlanEstudioAsignatura
# ---------------------------------------------------------------------------
class PlanEstudioAsignaturaListCreateView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    def get(self, request):
        items = PlanEstudioAsignatura.objects.select_related('plan_estudio', 'asignatura').all()
        plan_id = request.query_params.get('plan_estudio')
        if plan_id:
            items = items.filter(plan_estudio_id=plan_id)
        serializer = PlanEstudioAsignaturaSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PlanEstudioAsignaturaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlanEstudioAsignaturaDetailView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    def get(self, request, pk):
        item = get_object_or_404(PlanEstudioAsignatura, pk=pk)
        serializer = PlanEstudioAsignaturaSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        item = get_object_or_404(PlanEstudioAsignatura, pk=pk)
        serializer = PlanEstudioAsignaturaSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = get_object_or_404(PlanEstudioAsignatura, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Prerrequisito
# ---------------------------------------------------------------------------
class PrerrequisitoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Prerrequisito.objects.select_related('asignatura', 'asignatura_prerrequisito').all()
        asignatura_id = request.query_params.get('asignatura')
        if asignatura_id:
            items = items.filter(asignatura_id=asignatura_id)
        serializer = PrerrequisitoSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = PrerrequisitoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrerrequisitoDetailView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    def get(self, request, pk):
        item = get_object_or_404(Prerrequisito, pk=pk)
        serializer = PrerrequisitoSerializer(item)
        return Response(serializer.data)

    def delete(self, request, pk):
        item = get_object_or_404(Prerrequisito, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# HistorialAcademico
#
# Regla de visibilidad (importante):
# - Estudiante: solo puede ver SU PROPIO historial (no el de otros).
# - Jefe de Departamento / Administrador: pueden ver el historial de
#   cualquier estudiante (lo necesitan para validar matrículas), filtrando
#   opcionalmente por ?estudiante=<id>.
# ---------------------------------------------------------------------------
class HistorialAcademicoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rol = request.user.rol.nombre if request.user.rol else None
        items = HistorialAcademico.objects.select_related(
            'estudiante', 'asignatura', 'periodo_academico'
        ).all()

        if rol == 'Estudiante':
            # Un estudiante solo ve su propio historial, sin importar
            # qué filtro intente pasar por query params.
            items = items.filter(estudiante__usuario=request.user)
        else:
            estudiante_id = request.query_params.get('estudiante')
            if estudiante_id:
                items = items.filter(estudiante_id=estudiante_id)

        serializer = HistorialAcademicoSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Solo Jefe de Departamento/Administrador registran historial
        # (lo carga la institución, el estudiante no se autocalifica).
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = HistorialAcademicoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HistorialAcademicoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(HistorialAcademico, pk=pk)
        rol = request.user.rol.nombre if request.user.rol else None
        if rol == 'Estudiante' and item.estudiante.usuario_id != request.user.id:
            return Response(
                {'detail': 'No puedes ver el historial académico de otro estudiante.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = HistorialAcademicoSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        item = get_object_or_404(HistorialAcademico, pk=pk)
        serializer = HistorialAcademicoSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        item = get_object_or_404(HistorialAcademico, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)