"""
Views del bloque Usuarios: autenticación JWT y CRUD de entidades.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

from .models import Estudiante, JefeDepartamento, Docente
from .serializers import (
    SigmaTokenObtainPairSerializer, UsuarioSerializer,
    EstudianteSerializer, JefeDepartamentoSerializer, DocenteSerializer,
)
from .permissions import EsJefeDepartamentoOAdministrador


# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------
class LoginView(TokenObtainPairView):
    """
    POST /api/usuarios/login/
    body: {"correo": "...", "password": "..."}
    -> {"access": "...", "refresh": "...", "rol": "...", "correo": "...", "usuario_id": ...}
    """
    permission_classes = [AllowAny]
    serializer_class = SigmaTokenObtainPairSerializer


class LogoutView(APIView):
    """
    POST /api/usuarios/logout/
    body: {"refresh": "..."}
    Invalida el refresh token (requiere blacklist app activa).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Se requiere el campo "refresh".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {'detail': 'Token inválido o ya expirado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(APIView):
    """GET /api/usuarios/me/ -> datos del usuario autenticado actualmente."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Estudiante
# ---------------------------------------------------------------------------
class EstudianteListCreateView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    def get(self, request):
        estudiantes = Estudiante.objects.select_related('usuario', 'programa_academico').all()
        serializer = EstudianteSerializer(estudiantes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EstudianteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EstudianteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        estudiante = get_object_or_404(Estudiante, pk=pk)
        serializer = EstudianteSerializer(estudiante)
        return Response(serializer.data)

    def put(self, request, pk):
        estudiante = get_object_or_404(Estudiante, pk=pk)
        serializer = EstudianteSerializer(estudiante, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        estudiante = get_object_or_404(Estudiante, pk=pk)
        estudiante.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# JefeDepartamento
# ---------------------------------------------------------------------------
class JefeDepartamentoListCreateView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    def get(self, request):
        jefes = JefeDepartamento.objects.select_related('usuario', 'programa_academico').all()
        serializer = JefeDepartamentoSerializer(jefes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JefeDepartamentoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JefeDepartamentoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        jefe = get_object_or_404(JefeDepartamento, pk=pk)
        serializer = JefeDepartamentoSerializer(jefe)
        return Response(serializer.data)

    def put(self, request, pk):
        jefe = get_object_or_404(JefeDepartamento, pk=pk)
        serializer = JefeDepartamentoSerializer(jefe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        jefe = get_object_or_404(JefeDepartamento, pk=pk)
        jefe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Docente
# ---------------------------------------------------------------------------
class DocenteListCreateView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    def get(self, request):
        docentes = Docente.objects.select_related('programa_academico').all()
        serializer = DocenteSerializer(docentes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DocenteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocenteDetailView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    def get(self, request, pk):
        docente = get_object_or_404(Docente, pk=pk)
        serializer = DocenteSerializer(docente)
        return Response(serializer.data)

    def put(self, request, pk):
        docente = get_object_or_404(Docente, pk=pk)
        serializer = DocenteSerializer(docente, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        docente = get_object_or_404(Docente, pk=pk)
        docente.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)