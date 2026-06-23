"""
Vistas de carga de información académica vía CSV (CU02).

Según el Análisis Preliminar, el Jefe de Departamento carga 4 tipos de
información, cada uno en su propio archivo CSV (no se mezclan en un
solo archivo, porque cada uno tiene una estructura de columnas distinta):
  1. Asignaturas       -> POST /academico/cargar/asignaturas/
  2. Docentes           -> POST /usuarios/cargar/docentes/ (vive en la app
                            usuarios porque Docente está modelado ahí)
  3. Plan de estudio    -> POST /academico/cargar/plan-estudio/
  4. Historial académico -> POST /academico/cargar/historial-academico/

Todas las vistas:
- Exigen rol Jefe de Departamento o Administrador.
- Aceptan únicamente archivos .csv (Requisito Especial de CU02).
- Validan la estructura de columnas antes de procesar cualquier fila.
- Si CUALQUIER fila falla la validación, no se guarda nada parcial
  (atomicidad): se devuelve la lista completa de errores encontrados,
  fila por fila, para que el Jefe corrija el archivo y reintente.
- Un Jefe de Departamento solo puede cargar información que quede
  asociada a SU PROPIO programa académico (nunca se confía en lo que
  pueda venir en una columna 'programa_academico' del CSV, si la
  hubiera): se usa siempre jefe.programa_academico_id del usuario
  autenticado.
"""
import csv
import io

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import (
    Asignatura, PlanEstudio, PlanEstudioAsignatura, HistorialAcademico, PeriodoAcademico,
)
from usuarios.permissions import EsJefeDepartamentoOAdministrador
from usuarios.models import Estudiante


def _leer_filas_csv(archivo, columnas_requeridas):
    """
    Decodifica el archivo subido como CSV (utf-8) y valida que tenga
    exactamente las columnas requeridas en su encabezado.
    Devuelve (lista_de_filas_dict, error_o_None).
    """
    nombre = archivo.name or ''
    if not nombre.lower().endswith('.csv'):
        return None, 'El sistema solo acepta archivos en formato .csv.'

    try:
        contenido = archivo.read().decode('utf-8-sig')
    except UnicodeDecodeError:
        return None, 'No se pudo leer el archivo. Asegúrate de que esté guardado como CSV con codificación UTF-8.'

    lector = csv.DictReader(io.StringIO(contenido))
    columnas_encontradas = set(lector.fieldnames or [])
    faltantes = set(columnas_requeridas) - columnas_encontradas
    if faltantes:
        return None, f'El archivo no tiene las columnas requeridas: {", ".join(sorted(faltantes))}.'

    filas = list(lector)
    if len(filas) == 0:
        return None, 'El archivo no contiene ninguna fila de datos.'

    return filas, None


def _obtener_jefe_y_programa(request):
    """Devuelve (jefe_departamento, programa_academico_id) o (None, None)."""
    jefe = getattr(request.user, 'jefe_departamento', None)
    if jefe is None:
        return None, None
    return jefe, jefe.programa_academico_id


# ---------------------------------------------------------------------------
# 1) Carga de Asignaturas
# ---------------------------------------------------------------------------
class CargarAsignaturasView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    COLUMNAS_REQUERIDAS = ['codigo', 'nombre']

    def post(self, request):
        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response({'detail': 'Debes adjuntar un archivo CSV.'}, status=status.HTTP_400_BAD_REQUEST)

        filas, error = _leer_filas_csv(archivo, self.COLUMNAS_REQUERIDAS)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        errores = []
        for numero, fila in enumerate(filas, start=2):  # fila 1 es el encabezado
            codigo = (fila.get('codigo') or '').strip()
            nombre = (fila.get('nombre') or '').strip()
            if not codigo or not nombre:
                errores.append(f'Fila {numero}: "codigo" y "nombre" son obligatorios.')

        if errores:
            return Response({'detail': 'El archivo contiene errores.', 'errores': errores}, status=status.HTTP_400_BAD_REQUEST)

        creadas, actualizadas = 0, 0
        with transaction.atomic():
            for fila in filas:
                codigo = fila['codigo'].strip()
                nombre = fila['nombre'].strip()
                _, fue_creada = Asignatura.objects.update_or_create(
                    codigo=codigo, defaults={'nombre': nombre},
                )
                if fue_creada:
                    creadas += 1
                else:
                    actualizadas += 1

        return Response({
            'detail': 'Asignaturas cargadas exitosamente.',
            'creadas': creadas,
            'actualizadas': actualizadas,
            'total_filas': len(filas),
        }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# 2) Carga de Plan de Estudio (PlanEstudioAsignatura del plan vigente
#    del programa del Jefe que carga el archivo)
# ---------------------------------------------------------------------------
class CargarPlanEstudioView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    COLUMNAS_REQUERIDAS = ['codigo_asignatura', 'semestre', 'creditos']

    def post(self, request):
        jefe, programa_id = _obtener_jefe_y_programa(request)
        if programa_id is None:
            return Response(
                {'detail': 'Solo un Jefe de Departamento con programa académico asignado puede cargar el plan de estudio.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response({'detail': 'Debes adjuntar un archivo CSV.'}, status=status.HTTP_400_BAD_REQUEST)

        filas, error = _leer_filas_csv(archivo, self.COLUMNAS_REQUERIDAS)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        plan = PlanEstudio.objects.filter(programa_academico_id=programa_id, estado='vigente').first()
        if plan is None:
            return Response(
                {'detail': 'Tu programa académico no tiene un plan de estudios vigente. Crea uno primero desde el panel de administración.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        errores = []
        filas_validas = []
        for numero, fila in enumerate(filas, start=2):
            codigo_asignatura = (fila.get('codigo_asignatura') or '').strip()
            semestre_raw = (fila.get('semestre') or '').strip()
            creditos_raw = (fila.get('creditos') or '').strip()

            if not codigo_asignatura:
                errores.append(f'Fila {numero}: "codigo_asignatura" es obligatorio.')
                continue
            if not Asignatura.objects.filter(codigo=codigo_asignatura).exists():
                errores.append(f'Fila {numero}: no existe ninguna asignatura con código "{codigo_asignatura}". Cárgala primero.')
                continue
            if not semestre_raw.isdigit() or int(semestre_raw) < 1:
                errores.append(f'Fila {numero}: "semestre" debe ser un número entero positivo.')
                continue
            if not creditos_raw.isdigit() or int(creditos_raw) < 1:
                errores.append(f'Fila {numero}: "creditos" debe ser un número entero positivo.')
                continue

            filas_validas.append({
                'codigo_asignatura': codigo_asignatura,
                'semestre': int(semestre_raw),
                'creditos': int(creditos_raw),
            })

        if errores:
            return Response({'detail': 'El archivo contiene errores.', 'errores': errores}, status=status.HTTP_400_BAD_REQUEST)

        # 'reemplazar=true' borra TODAS las filas existentes de ESTE plan
        # (el del programa del Jefe autenticado) antes de insertar las
        # nuevas. Nunca toca el plan de estudios de otro programa.
        reemplazar = (request.data.get('reemplazar') or '').strip().lower() == 'true'
        eliminadas = 0

        creadas, actualizadas = 0, 0
        with transaction.atomic():
            if reemplazar:
                eliminadas, _ = PlanEstudioAsignatura.objects.filter(plan_estudio=plan).delete()
            for fila in filas_validas:
                asignatura = Asignatura.objects.get(codigo=fila['codigo_asignatura'])
                _, fue_creada = PlanEstudioAsignatura.objects.update_or_create(
                    plan_estudio=plan, asignatura=asignatura,
                    defaults={'semestre': fila['semestre'], 'creditos': fila['creditos']},
                )
                if fue_creada:
                    creadas += 1
                else:
                    actualizadas += 1

        return Response({
            'detail': f'Plan de estudio "{plan.nombre}" actualizado exitosamente.',
            'creadas': creadas,
            'actualizadas': actualizadas,
            'eliminadas': eliminadas,
            'total_filas': len(filas_validas),
        }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# 3) Carga de Historial Académico
# ---------------------------------------------------------------------------
class CargarHistorialAcademicoView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    COLUMNAS_REQUERIDAS = ['codigo_estudiante', 'codigo_asignatura', 'periodo_academico', 'estado']
    ESTADOS_VALIDOS = {choice[0] for choice in HistorialAcademico.ESTADO_CHOICES}

    def post(self, request):
        jefe, programa_id = _obtener_jefe_y_programa(request)
        if programa_id is None:
            return Response(
                {'detail': 'Solo un Jefe de Departamento con programa académico asignado puede cargar historial académico.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response({'detail': 'Debes adjuntar un archivo CSV.'}, status=status.HTTP_400_BAD_REQUEST)

        filas, error = _leer_filas_csv(archivo, self.COLUMNAS_REQUERIDAS)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        errores = []
        filas_validas = []
        for numero, fila in enumerate(filas, start=2):
            codigo_estudiante = (fila.get('codigo_estudiante') or '').strip()
            codigo_asignatura = (fila.get('codigo_asignatura') or '').strip()
            nombre_periodo = (fila.get('periodo_academico') or '').strip()
            estado_valor = (fila.get('estado') or '').strip()
            nota_raw = (fila.get('nota') or '').strip()

            # El estudiante debe existir Y pertenecer al programa del
            # Jefe que carga el archivo: un Jefe nunca puede cargar
            # historial de estudiantes de otra carrera.
            estudiante = Estudiante.objects.filter(codigo=codigo_estudiante, programa_academico_id=programa_id).first()
            if estudiante is None:
                errores.append(f'Fila {numero}: no existe un estudiante con código "{codigo_estudiante}" en tu programa académico.')
                continue

            asignatura = Asignatura.objects.filter(codigo=codigo_asignatura).first()
            if asignatura is None:
                errores.append(f'Fila {numero}: no existe ninguna asignatura con código "{codigo_asignatura}".')
                continue

            periodo = PeriodoAcademico.objects.filter(nombre=nombre_periodo).first()
            if periodo is None:
                errores.append(f'Fila {numero}: no existe ningún periodo académico llamado "{nombre_periodo}".')
                continue

            if estado_valor not in self.ESTADOS_VALIDOS:
                errores.append(f'Fila {numero}: "estado" debe ser uno de: {", ".join(sorted(self.ESTADOS_VALIDOS))}.')
                continue

            nota = None
            if nota_raw:
                try:
                    nota = float(nota_raw)
                except ValueError:
                    errores.append(f'Fila {numero}: "nota" debe ser un número (ej. 4.5).')
                    continue

            filas_validas.append({
                'estudiante': estudiante, 'asignatura': asignatura,
                'periodo_academico': periodo, 'estado': estado_valor, 'nota': nota,
            })

        if errores:
            return Response({'detail': 'El archivo contiene errores.', 'errores': errores}, status=status.HTTP_400_BAD_REQUEST)

        # 'reemplazar=true' borra TODO el historial académico existente
        # de los estudiantes de ESTE programa (nunca el de otro programa)
        # antes de insertar el nuevo.
        reemplazar = (request.data.get('reemplazar') or '').strip().lower() == 'true'
        eliminadas = 0

        creadas, actualizadas = 0, 0
        with transaction.atomic():
            if reemplazar:
                eliminadas, _ = HistorialAcademico.objects.filter(
                    estudiante__programa_academico_id=programa_id
                ).delete()
            for fila in filas_validas:
                _, fue_creada = HistorialAcademico.objects.update_or_create(
                    estudiante=fila['estudiante'], asignatura=fila['asignatura'],
                    periodo_academico=fila['periodo_academico'],
                    defaults={'estado': fila['estado'], 'nota': fila['nota']},
                )
                if fue_creada:
                    creadas += 1
                else:
                    actualizadas += 1

        return Response({
            'detail': 'Historial académico cargado exitosamente.',
            'creadas': creadas,
            'actualizadas': actualizadas,
            'eliminadas': eliminadas,
            'total_filas': len(filas_validas),
        }, status=status.HTTP_200_OK)