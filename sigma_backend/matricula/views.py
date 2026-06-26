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
from django.utils import timezone
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

        # Mismo criterio que ProgramacionAcademicaListCreateView: no se
        # confía en lo que el cliente envíe para 'jefe_departamento', se
        # toma siempre del usuario autenticado si es Jefe de Departamento.
        datos = request.data.copy()
        jefe_departamento = getattr(request.user, 'jefe_departamento', None)
        if jefe_departamento is not None:
            datos['jefe_departamento'] = jefe_departamento.id

        serializer = PeriodoMatriculaSerializer(data=datos)
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

        # No se permite modificar fechas/requisitos si ya está publicado,
        # salvo que la petición sea exactamente para reabrirlo (ver
        # PeriodoMatriculaReabrirView). Esto cierra el hueco de que antes
        # solo el frontend bloqueaba la edición tras publicar, pero la
        # API en sí no validaba nada.
        if item.estado == 'publicado':
            return Response(
                {'detail': 'No se puede modificar un periodo de matrícula ya publicado. Primero debes reabrirlo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

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


class PeriodoMatriculaReabrirView(APIView):
    """
    POST /api/matricula/periodos-matricula/<pk>/reabrir/

    Permite al Jefe de Departamento volver a abrir para edición un
    periodo de matrícula ya publicado, pero SOLO después de que su
    fecha_fin ya haya pasado (protege el proceso de matrícula mientras
    todavía está activo y en uso por los estudiantes). Al reabrir, el
    estado vuelve a 'no_publicado'; las fechas y requisitos documentales
    quedan editables de nuevo, y para que los estudiantes puedan volver
    a solicitar, el Jefe deberá publicarlo otra vez (con una fecha_fin
    actualizada).
    """
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    def post(self, request, pk):
        periodo = get_object_or_404(PeriodoMatricula, pk=pk)

        if periodo.estado != 'publicado':
            return Response(
                {'detail': 'Este periodo de matrícula no está publicado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hoy = timezone.localdate()
        if hoy <= periodo.fecha_fin:
            return Response(
                {
                    'detail': (
                        f'No puedes reabrir este periodo todavía: el plazo de solicitudes '
                        f'termina el {periodo.fecha_fin}. Podrás reabrirlo a partir del día siguiente.'
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        periodo.estado = 'no_publicado'
        periodo.save(update_fields=['estado', 'updated_at'])

        serializer = PeriodoMatriculaSerializer(periodo)
        return Response(serializer.data)


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
            # Un Jefe de Departamento solo ve solicitudes de estudiantes
            # de SU PROPIO programa académico (mismo criterio aplicado
            # ya a HistorialAcademico). Un Administrador ve todas.
            jefe = getattr(request.user, 'jefe_departamento', None)
            if jefe is not None:
                items = items.filter(estudiante__programa_academico_id=jefe.programa_academico_id)

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


class SolicitudMatriculaConfirmarEnvioView(APIView):
    """
    POST /api/matricula/solicitudes-matricula/<pk>/confirmar-envio/

    Marca la solicitud como 'enviada formalmente' (ver CU13 paso final,
    CU19 y CU20: una vez confirmado el envío, el Estudiante ya no puede
    modificar las asignaturas seleccionadas ni los documentos adjuntos;
    solo el Jefe de Departamento puede actuar sobre ella desde ahí).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudMatricula, pk=pk)

        if not _es_propietario_o_jefe(request, solicitud.estudiante):
            return Response(
                {'detail': 'No puedes confirmar el envío de la solicitud de otro estudiante.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if solicitud.enviada_formalmente:
            return Response(
                {'detail': 'Esta solicitud ya fue enviada formalmente.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if solicitud.estado != 'pendiente_revision':
            return Response(
                {'detail': 'Solo se puede confirmar el envío de una solicitud pendiente de revisión.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        asignaturas_count = solicitud.asignaturas_solicitadas.count()
        if asignaturas_count == 0:
            return Response(
                {'detail': 'Debes seleccionar al menos una asignatura antes de enviar tu solicitud.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ver CU12, paso 5 del flujo normal: "Sistema confirma que todos
        # los documentos requeridos han sido adjuntados" - esto debe
        # cumplirse antes de poder enviar formalmente la solicitud
        # (CU13), no solo validarse en el frontend.
        requisitos_ids = set(
            RequisitoDocumental.objects.filter(
                periodo_matricula=solicitud.periodo_matricula
            ).values_list('id', flat=True)
        )
        requisitos_con_documento = set(
            DocumentoAdjunto.objects.filter(
                solicitud_matricula=solicitud
            ).values_list('requisito_documental_id', flat=True)
        )
        requisitos_faltantes = requisitos_ids - requisitos_con_documento
        if requisitos_faltantes:
            nombres_faltantes = list(
                RequisitoDocumental.objects.filter(id__in=requisitos_faltantes).values_list('nombre', flat=True)
            )
            return Response(
                {
                    'detail': (
                        f'Debes adjuntar todos los documentos requeridos antes de enviar tu solicitud. '
                        f'Faltan: {", ".join(nombres_faltantes)}.'
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        solicitud.enviada_formalmente = True
        solicitud.save(update_fields=['enviada_formalmente', 'updated_at'])

        serializer = SolicitudMatriculaSerializer(solicitud)
        return Response(serializer.data)


class SolicitudMatriculaAprobarView(APIView):
    """
    POST /api/matricula/solicitudes-matricula/<pk>/aprobar/
    body opcional: {"confirmar_reemplazos": true}

    Flujo (ver Modelo de Negocio - Gestión de Matrícula Académica):
    1) Valida que la solicitud esté pendiente_revision.
    2) Por cada asignatura solicitada, detecta si el estudiante YA tiene
       esa misma asignatura aprobada en OTRA solicitud de este mismo
       periodo (de un intento anterior, ver num_intento):
         - Si es el MISMO grupo: no hay conflicto, simplemente no se
           vuelve a descontar cupo (ya lo estaba ocupando).
         - Si es OTRO grupo: es un "reemplazo de horario". Si el body
           no trae confirmar_reemplazos=true, se devuelve 409 con el
           detalle de qué se reemplazaría, SIN aprobar nada todavía.
           Si confirmar_reemplazos=true, se libera el cupo del grupo
           viejo, se descuenta el del nuevo, y se actualiza el 'grupo'
           de la SolicitudAsignatura de la solicitud anterior para que
           apunte al nuevo grupo (esa solicitud anterior se queda como
           'aprobada', solo cambia internamente a qué grupo apunta).
    3) Para asignaturas sin conflicto, valida cupo y descuenta normal.
    4) Marca la solicitud como 'aprobada'.
    5) Genera la MatriculaOficial (PDF) automáticamente.
    Todo dentro de una transacción: si algo falla, no se deja nada a medias.
    """
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    @transaction.atomic
    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudMatricula, pk=pk)
        confirmar_reemplazos = bool(request.data.get('confirmar_reemplazos'))

        # Un Jefe de Departamento solo puede aprobar solicitudes de
        # estudiantes de SU PROPIO programa académico.
        jefe = getattr(request.user, 'jefe_departamento', None)
        if jefe is not None and solicitud.estudiante.programa_academico_id != jefe.programa_academico_id:
            return Response(
                {'detail': 'No puedes aprobar solicitudes de estudiantes de otro programa académico.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if solicitud.estado != 'pendiente_revision':
            return Response(
                {'detail': 'Solo se puede aprobar una solicitud pendiente de revisión.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        asignaturas = list(
            solicitud.asignaturas_solicitadas.select_related('grupo', 'grupo__asignatura').all()
        )
        if not asignaturas:
            return Response(
                {'detail': 'La solicitud no tiene asignaturas seleccionadas.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------------------------
        # Detectar, por cada asignatura, si el estudiante ya la tiene
        # aprobada en OTRA solicitud de este mismo periodo de matrícula
        # (de un intento anterior), y en qué grupo.
        # -----------------------------------------------------------
        otras_aprobadas_del_periodo = SolicitudAsignatura.objects.filter(
            solicitud_matricula__estudiante=solicitud.estudiante,
            solicitud_matricula__periodo_matricula=solicitud.periodo_matricula,
            solicitud_matricula__estado='aprobada',
        ).exclude(solicitud_matricula=solicitud).select_related('grupo', 'grupo__asignatura', 'solicitud_matricula')

        aprobada_previa_por_asignatura = {}
        for sa_previa in otras_aprobadas_del_periodo:
            aprobada_previa_por_asignatura[sa_previa.grupo.asignatura_id] = sa_previa

        asignaturas_sin_conflicto = []
        reemplazos_a_confirmar = []  # (sa_nueva, sa_vieja) cuando cambia de grupo
        reemplazos_mismo_grupo = []  # sa_nueva cuando es exactamente el mismo grupo

        for sa in asignaturas:
            sa_previa = aprobada_previa_por_asignatura.get(sa.grupo.asignatura_id)
            if sa_previa is None:
                asignaturas_sin_conflicto.append(sa)
            elif sa_previa.grupo_id == sa.grupo_id:
                reemplazos_mismo_grupo.append(sa)
            else:
                reemplazos_a_confirmar.append((sa, sa_previa))

        # Si hay reemplazos de GRUPO DISTINTO y el Jefe todavía no confirmó,
        # se detiene aquí sin aprobar nada, devolviendo el detalle para que
        # el frontend pueda mostrar la advertencia y pedir confirmación.
        if reemplazos_a_confirmar and not confirmar_reemplazos:
            detalle_reemplazos = [
                {
                    'asignatura_codigo': sa_nueva.grupo.asignatura.codigo,
                    'asignatura_nombre': sa_nueva.grupo.asignatura.nombre,
                    'grupo_anterior': sa_vieja.grupo.nombre,
                    'grupo_nuevo': sa_nueva.grupo.nombre,
                    'solicitud_anterior_id': sa_vieja.solicitud_matricula_id,
                }
                for sa_nueva, sa_vieja in reemplazos_a_confirmar
            ]
            return Response(
                {
                    'detail': (
                        'Este estudiante ya tiene matriculadas algunas de estas asignaturas '
                        'en un grupo distinto, dentro de este mismo periodo. ¿Deseas reemplazar '
                        'el horario anterior por el nuevo?'
                    ),
                    'requiere_confirmacion': True,
                    'reemplazos': detalle_reemplazos,
                },
                status=status.HTTP_409_CONFLICT,
            )

        # Validar cupo disponible solo de los grupos que SÍ van a
        # descontar cupo nuevo (sin conflicto, o reemplazo confirmado).
        grupos_a_descontar = [sa.grupo for sa in asignaturas_sin_conflicto]
        grupos_a_descontar += [sa_nueva.grupo for sa_nueva, _ in reemplazos_a_confirmar]
        sin_cupo = [g for g in grupos_a_descontar if g.cupo_disponible <= 0]
        if sin_cupo:
            nombres = ', '.join(f'{g.asignatura.codigo} (grupo {g.nombre})' for g in sin_cupo)
            return Response(
                {'detail': f'No hay cupo disponible en: {nombres}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Descontar cupo de las asignaturas sin conflicto (caso normal).
        for sa in asignaturas_sin_conflicto:
            grupo = sa.grupo
            grupo.cupo_disponible -= 1
            grupo.save(update_fields=['cupo_disponible'])

        # Asignaturas que coinciden con el MISMO grupo de una aprobación
        # previa: no se vuelve a descontar cupo (el estudiante ya lo
        # ocupaba desde el intento anterior).

        # Reemplazos confirmados: liberar cupo del grupo viejo, descontar
        # el del nuevo, y mover la SolicitudAsignatura vieja al nuevo grupo
        # (la solicitud anterior se queda 'aprobada', solo cambia su grupo).
        for sa_nueva, sa_vieja in reemplazos_a_confirmar:
            grupo_viejo = sa_vieja.grupo
            grupo_nuevo = sa_nueva.grupo

            grupo_viejo.cupo_disponible += 1
            grupo_viejo.save(update_fields=['cupo_disponible'])

            grupo_nuevo.cupo_disponible -= 1
            grupo_nuevo.save(update_fields=['cupo_disponible'])

            sa_vieja.grupo = grupo_nuevo
            sa_vieja.save(update_fields=['grupo'])

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
        # No se adjunta el PDF directamente al correo: muchos servidores
        # de correo institucionales (ej. unicartagena.edu.co) bloquean o
        # descartan silenciosamente correos con adjuntos PDF provenientes
        # de remitentes externos, por políticas anti-malware (ver bug
        # real encontrado: el correo se "enviaba" exitosamente del lado
        # de Gmail, pero nunca llegaba a la bandeja institucional). En su
        # lugar, se envía el enlace directo de descarga del documento ya
        # almacenado (Cloudinary), evitando ese filtro por completo.
        notificar(
            usuario=solicitud.estudiante.usuario,
            tipo_evento='matricula_generada',
            mensaje=(
                f'Tu matrícula oficial para el periodo '
                f'{solicitud.periodo_matricula.periodo_academico.nombre} ya está disponible. '
                f'Puedes descargarla aquí: {matricula_oficial.documento.url}\n\n'
                'También puedes consultarla en cualquier momento desde SIGMA.'
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

        jefe = getattr(request.user, 'jefe_departamento', None)
        if jefe is not None and solicitud.estudiante.programa_academico_id != jefe.programa_academico_id:
            return Response(
                {'detail': 'No puedes rechazar solicitudes de estudiantes de otro programa académico.'},
                status=status.HTTP_403_FORBIDDEN,
            )

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
        if item.solicitud_matricula.enviada_formalmente:
            return Response(
                {'detail': 'Esta solicitud ya fue enviada formalmente y no puede modificarse.'},
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
        if item.solicitud_matricula.enviada_formalmente:
            return Response(
                {'detail': 'Esta solicitud ya fue enviada formalmente; no puedes modificar sus documentos.'},
                status=status.HTTP_400_BAD_REQUEST,
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