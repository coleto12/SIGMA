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
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

from .models import Estudiante, JefeDepartamento, Docente, Usuario
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


# ---------------------------------------------------------------------------
# Recuperación de contraseña
# ---------------------------------------------------------------------------
_generador_token_reset = PasswordResetTokenGenerator()


class SolicitarRecuperacionContrasenaView(APIView):
    """
    POST /api/usuarios/recuperar-contrasena/
    body: {"correo": "..."}

    Genera un enlace de restablecimiento y lo envía por correo. Por
    seguridad (no revelar si un correo existe o no en el sistema), esta
    vista SIEMPRE responde 200 con el mismo mensaje genérico, exista o
    no una cuenta con ese correo; si existe, además dispara el envío
    real del correo en segundo plano de la misma petición.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        correo = (request.data.get('correo') or '').strip().lower()
        if not correo:
            return Response({'detail': 'Debes indicar tu correo institucional.'}, status=status.HTTP_400_BAD_REQUEST)

        usuario = Usuario.objects.filter(correo=correo).first()
        if usuario is not None:
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = _generador_token_reset.make_token(usuario)
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
            enlace = f'{frontend_url}/restablecer-contrasena/{uid}/{token}'

            from notificaciones.services import _enviar_correo
            _enviar_correo(
                usuario=usuario,
                tipo_evento='recuperacion_contrasena',
                mensaje=(
                    'Recibimos una solicitud para restablecer tu contraseña en SIGMA.\n\n'
                    f'Si fuiste tú, ingresa a este enlace para crear una nueva contraseña:\n{enlace}\n\n'
                    'Este enlace expira en unos días. Si no solicitaste este cambio, '
                    'puedes ignorar este correo.'
                ),
            )

        # Mensaje idéntico exista o no el correo, para no filtrar qué
        # correos están registrados en el sistema.
        return Response({
            'detail': 'Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.',
        })


class ConfirmarRecuperacionContrasenaView(APIView):
    """
    POST /api/usuarios/restablecer-contrasena/
    body: {"uid": "...", "token": "...", "nueva_contrasena": "..."}

    Valida el uid/token generados en SolicitarRecuperacionContrasenaView
    y, si son válidos y no han expirado, actualiza la contraseña.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        nueva_contrasena = request.data.get('nueva_contrasena') or ''

        if not uid or not token or not nueva_contrasena:
            return Response(
                {'detail': 'Faltan datos para restablecer la contraseña.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(nueva_contrasena) < 8:
            return Response(
                {'detail': 'La nueva contraseña debe tener al menos 8 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            pk = force_str(urlsafe_base64_decode(uid))
            usuario = Usuario.objects.get(pk=pk)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            usuario = None

        if usuario is None or not _generador_token_reset.check_token(usuario, token):
            return Response(
                {'detail': 'El enlace de restablecimiento no es válido o ya expiró. Solicita uno nuevo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario.set_password(nueva_contrasena)
        usuario.save(update_fields=['password'])

        return Response({'detail': 'Tu contraseña fue restablecida exitosamente. Ya puedes iniciar sesión.'})