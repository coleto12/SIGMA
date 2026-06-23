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

        # El Jefe de Departamento solo puede crear programación académica
        # para SU PROPIO programa (ver JefeDepartamento.programa_academico,
        # relación fija 1 a 1). No se confía en lo que el cliente envíe en
        # el body para estos dos campos: se sobrescriben siempre con los
        # datos reales del usuario autenticado.
        datos = request.data.copy()
        jefe_departamento = getattr(request.user, 'jefe_departamento', None)
        if jefe_departamento is not None:
            datos['jefe_departamento'] = jefe_departamento.id
            datos['programa_academico'] = jefe_departamento.programa_academico_id

        serializer = ProgramacionAcademicaSerializer(data=datos)
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

            # Un Estudiante solo debe ver grupos de asignaturas que
            # pertenezcan a SU PROPIO plan de estudios (nunca los de
            # otra carrera, aunque esa programación también esté
            # publicada). Se resuelve el programa académico del
            # estudiante autenticado, nunca confiando en lo que venga
            # del cliente.
            estudiante = getattr(request.user, 'estudiante', None)
            if estudiante is not None:
                from academico.models import PlanEstudioAsignatura
                asignaturas_de_mi_plan = PlanEstudioAsignatura.objects.filter(
                    plan_estudio__programa_academico_id=estudiante.programa_academico_id,
                    plan_estudio__estado='vigente',
                ).values_list('asignatura_id', flat=True)
                grupos = grupos.filter(asignatura_id__in=asignaturas_de_mi_plan)

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
            grupo = serializer.save()
            from auditoria.utils import registrar_auditoria
            registrar_auditoria(
                request, accion='crear', modelo_afectado='Grupo', objeto_id=grupo.id,
                descripcion=f'Creó el grupo {grupo.nombre} de {grupo.asignatura.codigo} con docente {grupo.docente}.',
            )
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

        # CU09: no se puede modificar un grupo de una programación
        # académica que ya esté publicada (se necesitaría intervención
        # de un administrador del sistema, fuera del alcance actual).
        if grupo.programacion_academica.estado == 'publicada':
            return Response(
                {'detail': 'No se puede modificar un grupo de una programación académica ya publicada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        docente_anterior = grupo.docente_id
        cupo_anterior = grupo.cupo_maximo

        serializer = GrupoSerializer(grupo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            from auditoria.utils import registrar_auditoria
            cambios = []
            if 'docente' in request.data and grupo.docente_id != docente_anterior:
                cambios.append(f'docente (id {docente_anterior} -> {grupo.docente_id})')
            if 'cupo_maximo' in request.data and grupo.cupo_maximo != cupo_anterior:
                cambios.append(f'cupo máximo ({cupo_anterior} -> {grupo.cupo_maximo})')
            descripcion = f'Grupo {grupo.nombre} ({grupo.asignatura.codigo}): ' + (
                ', '.join(cambios) if cambios else 'sin cambios detectados'
            )
            registrar_auditoria(
                request, accion='modificar', modelo_afectado='Grupo',
                objeto_id=grupo.id, descripcion=descripcion,
            )

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        grupo = get_object_or_404(Grupo, pk=pk)

        if grupo.programacion_academica.estado == 'publicada':
            return Response(
                {'detail': 'No se puede eliminar un grupo de una programación académica ya publicada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # No se permite eliminar un grupo si algún estudiante ya lo
        # seleccionó en una solicitud de matrícula: borrarlo dejaría esa
        # solicitud con una referencia inválida / inconsistente.
        from matricula.models import SolicitudAsignatura
        if SolicitudAsignatura.objects.filter(grupo=grupo).exists():
            return Response(
                {'detail': 'No se puede eliminar este grupo: ya tiene estudiantes con solicitudes de matrícula asociadas.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from auditoria.utils import registrar_auditoria
        registrar_auditoria(
            request, accion='eliminar', modelo_afectado='Grupo',
            objeto_id=grupo.id, descripcion=f'Eliminó el grupo {grupo.nombre} de {grupo.asignatura.codigo}.',
        )

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
            horario = serializer.save()
            from auditoria.utils import registrar_auditoria
            registrar_auditoria(
                request, accion='crear', modelo_afectado='HorarioGrupo', objeto_id=horario.id,
                descripcion=f'Creó horario {horario.dia_semana} {horario.hora_inicio}-{horario.hora_fin} para el grupo {horario.grupo}.',
            )
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

        if horario.grupo.programacion_academica.estado == 'publicada':
            return Response(
                {'detail': 'No se puede modificar un horario de una programación académica ya publicada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        descripcion_anterior = f'{horario.dia_semana} {horario.hora_inicio}-{horario.hora_fin} en {horario.salon}'

        serializer = HorarioGrupoSerializer(horario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            from auditoria.utils import registrar_auditoria
            registrar_auditoria(
                request, accion='modificar', modelo_afectado='HorarioGrupo', objeto_id=horario.id,
                descripcion=f'Modificó horario del grupo {horario.grupo}: de "{descripcion_anterior}" a "{horario.dia_semana} {horario.hora_inicio}-{horario.hora_fin} en {horario.salon}".',
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]
        self.check_permissions(request)
        horario = get_object_or_404(HorarioGrupo, pk=pk)

        if horario.grupo.programacion_academica.estado == 'publicada':
            return Response(
                {'detail': 'No se puede eliminar un horario de una programación académica ya publicada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from auditoria.utils import registrar_auditoria
        registrar_auditoria(
            request, accion='eliminar', modelo_afectado='HorarioGrupo', objeto_id=horario.id,
            descripcion=f'Eliminó horario {horario.dia_semana} {horario.hora_inicio}-{horario.hora_fin} del grupo {horario.grupo}.',
        )

        horario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)