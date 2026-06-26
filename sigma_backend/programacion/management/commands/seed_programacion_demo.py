"""
Comando de un solo uso para preparar una ProgramacionAcademica lista
para publicar, con un Grupo + un HorarioGrupo para cada asignatura del
plan de estudios vigente de Ingeniería de Sistemas (ISIS) que TODAVÍA
NO TENGA un grupo creado en esta programación. Pensado para usarse
antes de una sustentación en vivo: solo falta hacer clic en "Publicar"
desde la interfaz.

NO es destructivo: nunca borra Grupos existentes (algunos pueden tener
SolicitudAsignatura reales de estudiantes que ya matricularon, y esas
relaciones son on_delete=PROTECT a propósito). Si una asignatura ya
tiene grupo en esta programación, se deja exactamente como está y
simplemente se completan las que faltan.

Uso:
    python manage.py seed_programacion_demo
"""
from datetime import time

from django.core.management.base import BaseCommand
from django.db import transaction

from institucional.models import ProgramaAcademico
from academico.models import PeriodoAcademico, PlanEstudio, PlanEstudioAsignatura
from usuarios.models import Docente
from programacion.models import ProgramacionAcademica, Grupo, HorarioGrupo, Salon


BLOQUES_HORARIO = [
    (time(7, 0), time(8, 40)),
    (time(8, 40), time(10, 20)),
    (time(10, 20), time(12, 0)),
    (time(14, 0), time(15, 40)),
    (time(15, 40), time(17, 20)),
]
DIAS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']


class Command(BaseCommand):
    help = 'Completa con Grupos + Horarios las asignaturas de ISIS que aún no tengan grupo en la programación vigente.'

    @transaction.atomic
    def handle(self, *args, **options):
        programa = ProgramaAcademico.objects.filter(codigo='ISIS').first()
        if programa is None:
            self.stderr.write(self.style.ERROR('No existe el programa académico ISIS. Corre seed_demo primero.'))
            return

        periodo_academico = PeriodoAcademico.objects.filter(nombre='2026-1').first()
        if periodo_academico is None:
            self.stderr.write(self.style.ERROR('No existe el periodo académico "2026-1". Corre seed_demo primero.'))
            return

        plan = PlanEstudio.objects.filter(programa_academico=programa, estado='vigente').first()
        if plan is None:
            self.stderr.write(self.style.ERROR('ISIS no tiene un plan de estudios vigente.'))
            return

        filas_plan = list(
            PlanEstudioAsignatura.objects.filter(plan_estudio=plan).select_related('asignatura').order_by('semestre', 'asignatura__codigo')
        )
        if not filas_plan:
            self.stderr.write(self.style.ERROR(
                'El plan de estudios vigente de ISIS no tiene asignaturas cargadas. '
                'Carga primero el CSV de plan de estudio desde "Carga de Información Académica".'
            ))
            return

        docentes = list(Docente.objects.filter(programa_academico=programa).order_by('codigo'))
        if not docentes:
            self.stderr.write(self.style.ERROR('ISIS no tiene docentes cargados. Carga primero el CSV de docentes.'))
            return

        salones = list(Salon.objects.all().order_by('nombre')[:50])
        if not salones:
            self.stderr.write(self.style.ERROR('No hay salones creados. Corre seed_salones primero.'))
            return

        # Reutiliza la ProgramacionAcademica de este periodo+programa si
        # ya existe (publicada o no); si no existe, la crea.
        programacion, fue_creada = ProgramacionAcademica.objects.get_or_create(
            programa_academico=programa,
            periodo_academico=periodo_academico,
            defaults={'estado': 'no_publicada'},
        )
        if not fue_creada and programacion.estado == 'publicada':
            self.stdout.write(self.style.WARNING(
                f'La programación del periodo {periodo_academico.nombre} ya estaba PUBLICADA. '
                'Se deja en estado "no_publicada" al final de este comando, para poder mostrar '
                'el proceso de publicación en vivo desde la interfaz.'
            ))

        # Asignaturas que YA tienen grupo en esta programación: se dejan
        # intactas (pueden tener SolicitudAsignatura reales apuntándoles,
        # protegidas con on_delete=PROTECT - nunca se tocan ni se borran).
        asignaturas_con_grupo = set(
            Grupo.objects.filter(programacion_academica=programacion).values_list('asignatura_id', flat=True)
        )
        filas_pendientes = [f for f in filas_plan if f.asignatura_id not in asignaturas_con_grupo]

        if not filas_pendientes:
            self.stdout.write(self.style.SUCCESS(
                'Todas las asignaturas del plan ya tienen grupo creado en esta programación. Nada que hacer.'
            ))
            return

        self.stdout.write(self.style.WARNING(
            f'{len(asignaturas_con_grupo)} asignatura(s) ya tenían grupo (se dejan intactas). '
            f'Creando grupos para las {len(filas_pendientes)} asignatura(s) restantes...'
        ))

        # -----------------------------------------------------------------
        # Antes de asignar horarios nuevos, hay que saber qué bloques
        # (día, hora, salón) y qué bloques por docente YA están ocupados
        # por los grupos existentes, para no generar cruces con ellos.
        # -----------------------------------------------------------------
        horarios_existentes = HorarioGrupo.objects.filter(
            grupo__programacion_academica=programacion
        ).select_related('grupo', 'salon')

        def _indice_bloque(hora_inicio, hora_fin):
            for idx, (hi, hf) in enumerate(BLOQUES_HORARIO):
                if hi == hora_inicio and hf == hora_fin:
                    return idx
            return None

        ocupacion_docente = {d.id: set() for d in docentes}
        ocupacion_salon = {}
        for h in horarios_existentes:
            idx = _indice_bloque(h.hora_inicio, h.hora_fin)
            if idx is None:
                continue  # horario con un bloque no estándar (creado manualmente) - se ignora para el cálculo de cruces nuevos
            ocupacion_docente.setdefault(h.grupo.docente_id, set()).add((h.dia_semana, idx))
            ocupacion_salon.setdefault((h.dia_semana, idx), set()).add(h.salon_id)

        grupos_creados = 0
        horarios_creados = 0

        for indice, fila in enumerate(filas_pendientes):
            asignatura = fila.asignatura
            docente = docentes[indice % len(docentes)]

            grupo = Grupo.objects.create(
                nombre='A',
                cupo_maximo=35,
                cupo_disponible=35,
                programacion_academica=programacion,
                asignatura=asignatura,
                docente=docente,
            )
            grupos_creados += 1

            combinaciones = [(dia, idx) for dia in DIAS for idx in range(len(BLOQUES_HORARIO))]
            offset = indice % len(combinaciones)
            combinaciones = combinaciones[offset:] + combinaciones[:offset]

            asignado = False
            for dia, bloque_idx in combinaciones:
                if (dia, bloque_idx) in ocupacion_docente.setdefault(docente.id, set()):
                    continue
                ocupados_en_bloque = ocupacion_salon.get((dia, bloque_idx), set())
                salon_libre = next((s for s in salones if s.id not in ocupados_en_bloque), None)
                if salon_libre is None:
                    continue

                hora_inicio, hora_fin = BLOQUES_HORARIO[bloque_idx]
                HorarioGrupo.objects.create(
                    grupo=grupo, dia_semana=dia,
                    hora_inicio=hora_inicio, hora_fin=hora_fin,
                    salon=salon_libre,
                )
                ocupacion_docente[docente.id].add((dia, bloque_idx))
                ocupacion_salon.setdefault((dia, bloque_idx), set()).add(salon_libre.id)
                horarios_creados += 1
                asignado = True
                break

            if not asignado:
                self.stdout.write(self.style.WARNING(
                    f'No se encontró un horario libre para "{asignatura.codigo}" (docente {docente.codigo}).'
                ))

        # Se deja siempre en 'no_publicada' al terminar, sin importar el
        # estado con el que estuviera antes: el propósito de este
        # comando es justamente dejar la oferta lista para publicarla
        # EN VIVO desde la interfaz (ej. durante una sustentación).
        programacion.estado = 'no_publicada'
        programacion.save(update_fields=['estado'])

        self.stdout.write(self.style.SUCCESS(
            f'Listo: se crearon {grupos_creados} grupos nuevos y {horarios_creados} horarios para '
            f'el periodo {periodo_academico.nombre} (ISIS), sin tocar los grupos existentes. '
            'La programación quedó en estado "no_publicada": ya puedes ir a '
            '"Publicar Información" y publicarla desde la interfaz.'
        ))