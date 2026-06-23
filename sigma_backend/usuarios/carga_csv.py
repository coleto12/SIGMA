"""
Vista de carga de Docentes vía CSV (parte de CU02 - Carga de Información
Académica). Vive en la app "usuarios" porque el modelo Docente está aquí.

Ver academico/carga_csv.py para el resto de las cargas (Asignaturas,
Plan de Estudio, Historial Académico) y la explicación general del
patrón de validación/atomicidad/seguridad que comparten todas.
"""
import csv
import io

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Docente
from .permissions import EsJefeDepartamentoOAdministrador


def _leer_filas_csv(archivo, columnas_requeridas):
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


class CargarDocentesView(APIView):
    permission_classes = [IsAuthenticated, EsJefeDepartamentoOAdministrador]

    COLUMNAS_REQUERIDAS = ['codigo', 'primer_nombre', 'primer_apellido', 'correo']
    COLUMNAS_OPCIONALES = ['segundo_nombre', 'segundo_apellido']

    def post(self, request):
        # Igual criterio que en programacion/academico: el docente queda
        # asociado SIEMPRE al programa académico del Jefe autenticado,
        # nunca a uno que pudiera venir en el CSV.
        jefe = getattr(request.user, 'jefe_departamento', None)
        if jefe is None:
            return Response(
                {'detail': 'Solo un Jefe de Departamento con programa académico asignado puede cargar docentes.'},
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
            codigo = (fila.get('codigo') or '').strip()
            primer_nombre = (fila.get('primer_nombre') or '').strip()
            primer_apellido = (fila.get('primer_apellido') or '').strip()
            correo = (fila.get('correo') or '').strip()

            if not codigo or not primer_nombre or not primer_apellido or not correo:
                errores.append(
                    f'Fila {numero}: "codigo", "primer_nombre", "primer_apellido" y "correo" son obligatorios.'
                )
                continue
            if '@' not in correo:
                errores.append(f'Fila {numero}: "{correo}" no parece un correo válido.')
                continue

            filas_validas.append({
                'codigo': codigo,
                'primer_nombre': primer_nombre,
                'segundo_nombre': (fila.get('segundo_nombre') or '').strip() or None,
                'primer_apellido': primer_apellido,
                'segundo_apellido': (fila.get('segundo_apellido') or '').strip() or None,
                'correo': correo,
            })

        if errores:
            return Response({'detail': 'El archivo contiene errores.', 'errores': errores}, status=status.HTTP_400_BAD_REQUEST)

        # 'reemplazar=true' borra TODOS los docentes existentes de ESTE
        # programa (nunca los de otro programa) antes de insertar los
        # nuevos. Si algún docente ya tiene grupos asignados, no se borra
        # nada y se informa cuáles bloquean el reemplazo (evita dejar
        # Grupo.docente apuntando a un registro eliminado).
        reemplazar = (request.data.get('reemplazar') or '').strip().lower() == 'true'
        eliminados = 0

        if reemplazar:
            docentes_del_programa = Docente.objects.filter(programa_academico_id=jefe.programa_academico_id)
            from programacion.models import Grupo
            docentes_con_grupos = docentes_del_programa.filter(grupo__isnull=False).distinct()
            if docentes_con_grupos.exists():
                nombres = ', '.join(
                    f'{d.primer_nombre} {d.primer_apellido} ({d.codigo})' for d in docentes_con_grupos
                )
                return Response(
                    {'detail': f'No se puede reemplazar: los siguientes docentes ya tienen grupos asignados: {nombres}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        creados, actualizados = 0, 0
        with transaction.atomic():
            if reemplazar:
                eliminados, _ = docentes_del_programa.delete()
            for fila in filas_validas:
                codigo = fila.pop('codigo')
                _, fue_creado = Docente.objects.update_or_create(
                    codigo=codigo,
                    defaults={**fila, 'programa_academico_id': jefe.programa_academico_id},
                )
                if fue_creado:
                    creados += 1
                else:
                    actualizados += 1

        return Response({
            'detail': 'Docentes cargados exitosamente.',
            'creados': creados,
            'actualizados': actualizados,
            'eliminados': eliminados,
            'total_filas': len(filas_validas),
        }, status=status.HTTP_200_OK)