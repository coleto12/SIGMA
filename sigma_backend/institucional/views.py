"""
Views del bloque Institucional, implementadas con APIView (estilo manual).

Patrón repetido para cada modelo:
- <Modelo>ListCreateView: GET (listar todos) / POST (crear uno nuevo)
- <Modelo>DetailView: GET (uno) / PUT (actualizar) / DELETE (eliminar)

Permisos (ver RNF-SEG-03 del ERS - RBAC):
- Lectura (GET): cualquier usuario autenticado (Estudiante, Jefe, Admin).
- Escritura (POST/PUT/DELETE): solo Jefe de Departamento o Administrador,
  ya que estas son tablas de estructura institucional, no algo que un
  Estudiante deba poder alterar.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Campus, Facultad, NivelFormacion, ProgramaAcademico
from .serializers import (
    CampusSerializer, FacultadSerializer,
    NivelFormacionSerializer, ProgramaAcademicoSerializer,
)
from usuarios.permissions import EsJefeDepartamentoOAdministrador


# ---------------------------------------------------------------------------
# Campus
# ---------------------------------------------------------------------------
class CampusListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        campus = Campus.objects.all()
        serializer = CampusSerializer(campus, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = CampusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CampusDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        campus = get_object_or_404(Campus, pk=pk)
        serializer = CampusSerializer(campus)
        return Response(serializer.data)

    def put(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        campus = get_object_or_404(Campus, pk=pk)
        serializer = CampusSerializer(campus, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        campus = get_object_or_404(Campus, pk=pk)
        campus.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Facultad
# ---------------------------------------------------------------------------
class FacultadListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        facultades = Facultad.objects.select_related('campus').all()
        serializer = FacultadSerializer(facultades, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = FacultadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacultadDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        facultad = get_object_or_404(Facultad, pk=pk)
        serializer = FacultadSerializer(facultad)
        return Response(serializer.data)

    def put(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        facultad = get_object_or_404(Facultad, pk=pk)
        serializer = FacultadSerializer(facultad, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        facultad = get_object_or_404(Facultad, pk=pk)
        facultad.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# NivelFormacion
# ---------------------------------------------------------------------------
class NivelFormacionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        niveles = NivelFormacion.objects.all()
        serializer = NivelFormacionSerializer(niveles, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = NivelFormacionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NivelFormacionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        nivel = get_object_or_404(NivelFormacion, pk=pk)
        serializer = NivelFormacionSerializer(nivel)
        return Response(serializer.data)

    def put(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        nivel = get_object_or_404(NivelFormacion, pk=pk)
        serializer = NivelFormacionSerializer(nivel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        nivel = get_object_or_404(NivelFormacion, pk=pk)
        nivel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# ProgramaAcademico
# ---------------------------------------------------------------------------
class ProgramaAcademicoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        programas = ProgramaAcademico.objects.select_related(
            'facultad', 'nivel_formacion'
        ).all()
        serializer = ProgramaAcademicoSerializer(programas, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = ProgramaAcademicoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProgramaAcademicoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        programa = get_object_or_404(ProgramaAcademico, pk=pk)
        serializer = ProgramaAcademicoSerializer(programa)
        return Response(serializer.data)

    def put(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        programa = get_object_or_404(ProgramaAcademico, pk=pk)
        serializer = ProgramaAcademicoSerializer(programa, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        programa = get_object_or_404(ProgramaAcademico, pk=pk)
        programa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)