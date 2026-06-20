"""
Views del bloque Matrícula Académica.

Incluye el flujo de negocio completo:
- Estudiante crea SolicitudMatricula y le agrega SolicitudAsignatura.
- Estudiante adjunta DocumentoAdjunto.
- Jefe de Departamento aprueba o rechaza la solicitud.
- Al aprobar: se valida cupo disponible, se descuenta cupo_disponible
  del Grupo, y se genera la MatriculaOficial (PDF) automáticamente.
"""
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import (
    PeriodoMatricula, RequisitoDocumental, SolicitudMatricula,
    SolicitudAsignatura, DocumentoAdjunto, MatriculaOficial,
)
from .serializers import (
    PeriodoMatriculaSerializer, RequisitoDocumentalSerializer,
    SolicitudMatriculaSerializer, SolicitudAsignaturaSerializer,
    DocumentoAdjuntoSerializer, MatriculaOficialSerializer,
)
from .pdf_utils import generar_pdf_matricula_oficial
from usuarios.permissions import EsJefeDepartamentoOAdministrador
from notificaciones.services import notificar


def _es_jefe_o_admin(request):
    rol = request.user.rol.nombre if request.user.rol else None
    return rol in ('Jefe de Departamento', 'Administrador')


def _es_propietario_o_jefe(request, estudiante):
    """True si el usuario es el propio estudiante dueño del registro, o Jefe/Admin."""
    if _es_jefe_o_admin(request):
        return True
    return estudiante.usuario_id == request.user.id


# ---------------------------------------------------------------------------
# PeriodoMatricula
# ---------------------------------------------------------------------------
class PeriodoMatriculaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = PeriodoMatricula.objects.select_related('periodo_academico', 'jefe_departamento').all()
        if not _es_jefe_o_admin(request):
            items = items.filter(estado='publicado')
        serializer = PeriodoMatriculaSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = PeriodoMatriculaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PeriodoMatriculaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(PeriodoMatricula, pk=pk)
        serializer = PeriodoMatriculaSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        item = get_object_or_404(PeriodoMatricula, pk=pk)
        serializer = PeriodoMatriculaSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        item = get_object_or_404(PeriodoMatricula, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# RequisitoDocumental
# ---------------------------------------------------------------------------
class RequisitoDocumentalListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = RequisitoDocumental.objects.select_related('periodo_matricula').all()
        periodo_id = request.query_params.get('periodo_matricula')
        if periodo_id:
            items = items.filter(periodo_matricula_id=periodo_id)
        serializer = RequisitoDocumentalSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        serializer = RequisitoDocumentalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequisitoDocumentalDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(RequisitoDocumental, pk=pk)
        serializer = RequisitoDocumentalSerializer(item)
        return Response(serializer.data)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        item = get_object_or_404(RequisitoDocumental, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# SolicitudMatricula
#
# Visibilidad: un Estudiante solo ve SUS PROPIAS solicitudes. Jefe/Admin ven
# todas (opcionalmente filtradas por ?estudiante= o ?periodo_matricula=).
# ---------------------------------------------------------------------------
class SolicitudMatriculaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = SolicitudMatricula.objects.select_related(
            'estudiante', 'periodo_matricula'
        ).all()

        if not _es_jefe_o_admin(request):
            items = items.filter(estudiante__usuario=request.user)
        else:
            estudiante_id = request.query_params.get('estudiante')
            if estudiante_id:
                items = items.filter(estudiante_id=estudiante_id)

        periodo_id = request.query_params.get('periodo_matricula')
        if periodo_id:
            items = items.filter(periodo_matricula_id=periodo_id)
        estado = request.query_params.get('estado')
        if estado:
            items = items.filter(estado=estado)

        serializer = SolicitudMatriculaSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SolicitudMatriculaSerializer(data=request.data)
        if serializer.is_valid():
            # Un Estudiante solo puede crear solicitudes para sí mismo.
            estudiante = serializer.validated_data['estudiante']
            if not _es_propietario_o_jefe(request, estudiante):
                return Response(
                    {'detail': 'No puedes crear una solicitud de matrícula para otro estudiante.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer.save()
            notificar(
                usuario=estudiante.usuario,
                tipo_evento='solicitud_recibida',
                mensaje=(
                    f'Tu solicitud de matrícula #{serializer.instance.pk} '
                    f'(intento {serializer.instance.num_intento}) fue registrada '
                    'y está pendiente de revisión.'
                ),
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SolicitudMatriculaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(SolicitudMatricula, pk=pk)
        if not _es_propietario_o_jefe(request, item.estudiante):
            return Response(
                {'detail': 'No puedes ver la solicitud de matrícula de otro estudiante.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = SolicitudMatriculaSerializer(item)
        return Response(serializer.data)

    def delete(self, request, pk):
        item = get_object_or_404(SolicitudMatricula, pk=pk)
        if not _es_propietario_o_jefe(request, item.estudiante):
            return Response(
                {'detail': 'No puedes eliminar la solicitud de matrícula de otro estudiante.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if item.estado != 'pendiente_revision':
            return Response(
                {'detail': 'Solo se puede eliminar una solicitud que esté pendiente de revisión.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SolicitudMatriculaAprobarView(APIView):
    """
    POST /api/matricula/solicitudes-matricula/<pk>/aprobar/

    Flujo (ver Modelo de Negocio - Gestión de Matrícula Académica):
    1) Valida que la solicitud esté pendiente_revision.
    2) Valida que cada grupo solicitado tenga cupo_disponible > 0.
    3) Descuenta cupo_disponible de cada Grupo.
    4) Marca la solicitud como 'aprobada'.
    5) Genera la MatriculaOficial (PDF) automáticamente.
    Todo dentro de una transacción: si algo falla, no se deja nada a medias.
    """
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    @transaction.atomic
    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudMatricula, pk=pk)

        if solicitud.estado != 'pendiente_revision':
            return Response(
                {'detail': 'Solo se puede aprobar una solicitud pendiente de revisión.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        asignaturas = list(
            solicitud.asignaturas_solicitadas.select_related('grupo').all()
        )
        if not asignaturas:
            return Response(
                {'detail': 'La solicitud no tiene asignaturas seleccionadas.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar cupo disponible de TODOS los grupos antes de descontar nada.
        sin_cupo = [
            sa.grupo for sa in asignaturas if sa.grupo.cupo_disponible <= 0
        ]
        if sin_cupo:
            nombres = ', '.join(f'{g.asignatura.codigo} (grupo {g.nombre})' for g in sin_cupo)
            return Response(
                {'detail': f'No hay cupo disponible en: {nombres}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Descontar cupo de cada grupo.
        for sa in asignaturas:
            grupo = sa.grupo
            grupo.cupo_disponible -= 1
            grupo.save(update_fields=['cupo_disponible'])

        solicitud.estado = 'aprobada'
        solicitud.motivo_rechazo = None
        solicitud.save(update_fields=['estado', 'motivo_rechazo', 'updated_at'])

        # Generar la matrícula oficial (PDF) automáticamente.
        jefe_departamento = getattr(request.user, 'jefe_departamento', None)
        archivo_pdf = generar_pdf_matricula_oficial(solicitud)
        matricula_oficial = MatriculaOficial(
            solicitud_matricula=solicitud,
            jefe_departamento=jefe_departamento,
        )
        matricula_oficial.documento.save(archivo_pdf.name, archivo_pdf, save=True)

        notificar(
            usuario=solicitud.estudiante.usuario,
            tipo_evento='solicitud_aprobada',
            mensaje=f'Tu solicitud de matrícula #{solicitud.pk} fue aprobada.',
        )
        notificar(
            usuario=solicitud.estudiante.usuario,
            tipo_evento='matricula_generada',
            mensaje=(
                f'Tu matrícula oficial para el periodo '
                f'{solicitud.periodo_matricula.periodo_academico.nombre} ya está disponible.'
            ),
        )

        serializer = SolicitudMatriculaSerializer(solicitud)
        return Response(serializer.data)


class SolicitudMatriculaRechazarView(APIView):
    """
    POST /api/matricula/solicitudes-matricula/<pk>/rechazar/
    body: {"motivo_rechazo": "..."}
    """
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudMatricula, pk=pk)

        if solicitud.estado != 'pendiente_revision':
            return Response(
                {'detail': 'Solo se puede rechazar una solicitud pendiente de revisión.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        motivo = request.data.get('motivo_rechazo')
        if not motivo:
            return Response(
                {'detail': 'Se requiere especificar el motivo del rechazo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        solicitud.estado = 'rechazada'
        solicitud.motivo_rechazo = motivo
        solicitud.save(update_fields=['estado', 'motivo_rechazo', 'updated_at'])

        notificar(
            usuario=solicitud.estudiante.usuario,
            tipo_evento='solicitud_rechazada',
            mensaje=f'Tu solicitud de matrícula #{solicitud.pk} fue rechazada. Motivo: {motivo}',
        )

        serializer = SolicitudMatriculaSerializer(solicitud)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# SolicitudAsignatura
# ---------------------------------------------------------------------------
class SolicitudAsignaturaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = SolicitudAsignatura.objects.select_related(
            'solicitud_matricula', 'grupo', 'grupo__asignatura'
        ).all()
        solicitud_id = request.query_params.get('solicitud_matricula')
        if solicitud_id:
            items = items.filter(solicitud_matricula_id=solicitud_id)

        if not _es_jefe_o_admin(request):
            items = items.filter(solicitud_matricula__estudiante__usuario=request.user)

        serializer = SolicitudAsignaturaSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SolicitudAsignaturaSerializer(data=request.data)
        if serializer.is_valid():
            solicitud = serializer.validated_data['solicitud_matricula']
            if not _es_propietario_o_jefe(request, solicitud.estudiante):
                return Response(
                    {'detail': 'No puedes modificar la solicitud de matrícula de otro estudiante.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SolicitudAsignaturaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(SolicitudAsignatura, pk=pk)
        if not _es_propietario_o_jefe(request, item.solicitud_matricula.estudiante):
            return Response(
                {'detail': 'No tienes acceso a este recurso.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = SolicitudAsignaturaSerializer(item)
        return Response(serializer.data)

    def delete(self, request, pk):
        item = get_object_or_404(SolicitudAsignatura, pk=pk)
        if not _es_propietario_o_jefe(request, item.solicitud_matricula.estudiante):
            return Response(
                {'detail': 'No tienes acceso a este recurso.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if item.solicitud_matricula.estado != 'pendiente_revision':
            return Response(
                {'detail': 'Solo se pueden quitar asignaturas de una solicitud pendiente de revisión.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# DocumentoAdjunto
# ---------------------------------------------------------------------------
class DocumentoAdjuntoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = DocumentoAdjunto.objects.select_related(
            'solicitud_matricula', 'requisito_documental'
        ).all()
        solicitud_id = request.query_params.get('solicitud_matricula')
        if solicitud_id:
            items = items.filter(solicitud_matricula_id=solicitud_id)

        if not _es_jefe_o_admin(request):
            items = items.filter(solicitud_matricula__estudiante__usuario=request.user)

        serializer = DocumentoAdjuntoSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DocumentoAdjuntoSerializer(data=request.data)
        if serializer.is_valid():
            solicitud = serializer.validated_data['solicitud_matricula']
            if not _es_propietario_o_jefe(request, solicitud.estudiante):
                return Response(
                    {'detail': 'No puedes adjuntar documentos a la solicitud de otro estudiante.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentoAdjuntoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(DocumentoAdjunto, pk=pk)
        if not _es_propietario_o_jefe(request, item.solicitud_matricula.estudiante):
            return Response(
                {'detail': 'No tienes acceso a este recurso.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = DocumentoAdjuntoSerializer(item)
        return Response(serializer.data)

    def delete(self, request, pk):
        item = get_object_or_404(DocumentoAdjunto, pk=pk)
        if not _es_propietario_o_jefe(request, item.solicitud_matricula.estudiante):
            return Response(
                {'detail': 'No tienes acceso a este recurso.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# MatriculaOficial (solo lectura vía API: se genera automáticamente al aprobar)
# ---------------------------------------------------------------------------
class MatriculaOficialListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = MatriculaOficial.objects.select_related(
            'solicitud_matricula', 'solicitud_matricula__estudiante'
        ).all()
        if not _es_jefe_o_admin(request):
            items = items.filter(solicitud_matricula__estudiante__usuario=request.user)
        serializer = MatriculaOficialSerializer(items, many=True)
        return Response(serializer.data)


class MatriculaOficialDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(MatriculaOficial, pk=pk)
        if not _es_propietario_o_jefe(request, item.solicitud_matricula.estudiante):
            return Response(
                {'detail': 'No tienes acceso a este recurso.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = MatriculaOficialSerializer(item)
        return Response(serializer.data)