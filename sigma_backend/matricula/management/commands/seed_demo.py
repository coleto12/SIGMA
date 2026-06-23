"""
Comando de management para poblar datos de prueba (demo end-to-end).

Uso:
    python manage.py seed_demo

Es idempotente: usa get_or_create en todos los pasos, así que se puede
correr varias veces sin duplicar registros ni romper nada.

Reutiliza el Estudiante y el Programa Académico que ya existan en la BD
(los busca por código/nombre) en lugar de crear datos duplicados; si no
los encuentra, los crea desde cero.
"""
from datetime import date, timedelta, time

from django.core.management.base import BaseCommand
from django.db import transaction

from institucional.models import Campus, Facultad, NivelFormacion, ProgramaAcademico
from usuarios.models import Rol, Usuario, Estudiante, JefeDepartamento, Docente
from academico.models import PeriodoAcademico, Asignatura, Prerrequisito, HistorialAcademico
from programacion.models import ProgramacionAcademica, Salon, Grupo, HorarioGrupo
from matricula.models import PeriodoMatricula, RequisitoDocumental


class Command(BaseCommand):
    help = 'Crea datos de prueba para validar el flujo completo de matrícula.'

    @transaction.atomic
    def handle(self, *args, **options):
        hoy = date.today()

        # -----------------------------------------------------------------
        # 1) Institucional: reutiliza si ya existe, crea si no.
        # -----------------------------------------------------------------
        campus, _ = Campus.objects.get_or_create(
            nombre='Piedra de Bolívar',
            defaults={'direccion': 'Cartagena de Indias'},
        )
        facultad, _ = Facultad.objects.get_or_create(
            nombre='Ingeniería', defaults={'campus': campus},
        )
        nivel, _ = NivelFormacion.objects.get_or_create(nombre='Pregrado')
        programa, _ = ProgramaAcademico.objects.get_or_create(
            codigo='ISIS',
            defaults={
                'nombre': 'Ingeniería de Sistemas',
                'facultad': facultad,
                'nivel_formacion': nivel,
            },
        )
        self.stdout.write(self.style.SUCCESS(f'Programa académico: {programa}'))

        # -----------------------------------------------------------------
        # 2) Roles
        # -----------------------------------------------------------------
        rol_estudiante, _ = Rol.objects.get_or_create(nombre='Estudiante')
        rol_jefe, _ = Rol.objects.get_or_create(nombre='Jefe de Departamento')

        # -----------------------------------------------------------------
        # 3) Jefe de Departamento (usuario nuevo de prueba)
        # -----------------------------------------------------------------
        usuario_jefe, creado = Usuario.objects.get_or_create(
            correo='jefe.isis@unicartagena.edu.co',
            defaults={'rol': rol_jefe, 'is_active': True},
        )
        if creado:
            usuario_jefe.set_password('Jefe12345')
            usuario_jefe.save()
            self.stdout.write(self.style.SUCCESS(
                'Usuario Jefe creado: jefe.isis@unicartagena.edu.co / contraseña: Jefe12345'
            ))
        else:
            usuario_jefe.rol = rol_jefe
            usuario_jefe.save(update_fields=['rol'])

        jefe_departamento, _ = JefeDepartamento.objects.get_or_create(
            usuario=usuario_jefe,
            defaults={
                'primer_nombre': 'Carlos',
                'primer_apellido': 'Ramírez',
                'codigo': 'JEFE001',
                'programa_academico': programa,
            },
        )

        # -----------------------------------------------------------------
        # 4) Estudiante: reutiliza el que ya existe (buscado por código).
        # -----------------------------------------------------------------
        try:
            estudiante = Estudiante.objects.get(codigo='0222320027')
            self.stdout.write(self.style.SUCCESS(f'Estudiante reutilizado: {estudiante}'))
        except Estudiante.DoesNotExist:
            usuario_estudiante, creado = Usuario.objects.get_or_create(
                correo='estudiante.demo@unicartagena.edu.co',
                defaults={'rol': rol_estudiante, 'is_active': True},
            )
            if creado:
                usuario_estudiante.set_password('Estudiante123')
                usuario_estudiante.save()
            estudiante = Estudiante.objects.create(
                primer_nombre='Estudiante',
                primer_apellido='Demo',
                telefono='3000000000',
                codigo='DEMO0001',
                semestre_actual=3,
                usuario=usuario_estudiante,
                programa_academico=programa,
            )
            self.stdout.write(self.style.SUCCESS(f'Estudiante creado: {estudiante}'))

        # -----------------------------------------------------------------
        # 5) Docente
        # -----------------------------------------------------------------
        docente, _ = Docente.objects.get_or_create(
            codigo='DOC001',
            defaults={
                'primer_nombre': 'Laura',
                'primer_apellido': 'Martínez',
                'correo': 'laura.martinez@unicartagena.edu.co',
                'programa_academico': programa,
            },
        )

        # -----------------------------------------------------------------
        # 6) Periodo académico vigente (hoy cae dentro del rango)
        # -----------------------------------------------------------------
        periodo_academico, _ = PeriodoAcademico.objects.get_or_create(
            nombre='2026-1',
            defaults={
                'fecha_inicio': hoy - timedelta(days=30),
                'fecha_fin': hoy + timedelta(days=120),
                'estado': 'activo',
            },
        )

        # -----------------------------------------------------------------
        # 7) Asignaturas + Prerrequisito
        #    "Programación I" (base) -> prerrequisito de "Programación II"
        # -----------------------------------------------------------------
        prog1, _ = Asignatura.objects.get_or_create(
            codigo='ISIS-101', defaults={'nombre': 'Programación I'},
        )
        prog2, _ = Asignatura.objects.get_or_create(
            codigo='ISIS-102', defaults={'nombre': 'Programación II'},
        )
        Prerrequisito.objects.get_or_create(
            asignatura=prog2, asignatura_prerrequisito=prog1,
        )

        # Asignatura adicional con prerrequisito NO cumplido por el estudiante
        # (sirve para probar que la validación rechaza correctamente).
        calculo1, _ = Asignatura.objects.get_or_create(
            codigo='MATE-101', defaults={'nombre': 'Cálculo I'},
        )
        calculo2, _ = Asignatura.objects.get_or_create(
            codigo='MATE-102', defaults={'nombre': 'Cálculo II'},
        )
        Prerrequisito.objects.get_or_create(
            asignatura=calculo2, asignatura_prerrequisito=calculo1,
        )
        # Nota: a propósito NO se crea HistorialAcademico de Cálculo I para
        # este estudiante, así que Cálculo II debe rechazarse al solicitarla.

        # El estudiante YA aprobó Programación I en un periodo anterior,
        # para que la validación de prerrequisito de Programación II pase.
        periodo_anterior, _ = PeriodoAcademico.objects.get_or_create(
            nombre='2025-2',
            defaults={
                'fecha_inicio': hoy - timedelta(days=200),
                'fecha_fin': hoy - timedelta(days=60),
                'estado': 'cerrado',
            },
        )
        HistorialAcademico.objects.get_or_create(
            estudiante=estudiante, asignatura=prog1, periodo_academico=periodo_anterior,
            defaults={'nota': 4.0, 'estado': 'aprobada'},
        )
        self.stdout.write(self.style.SUCCESS(
            'Historial académico: Programación I -> aprobada (cumple prerrequisito de Programación II)'
        ))

        # -----------------------------------------------------------------
        # 8) Salón
        # -----------------------------------------------------------------
        salon, _ = Salon.objects.get_or_create(
            nombre='Aula 301', defaults={'capacidad': 30, 'campus': campus},
        )

        # -----------------------------------------------------------------
        # 9) Programación académica (publicada) + Grupos + Horarios
        # -----------------------------------------------------------------
        programacion_academica, _ = ProgramacionAcademica.objects.get_or_create(
            programa_academico=programa, periodo_academico=periodo_academico,
            defaults={'estado': 'publicada', 'jefe_departamento': jefe_departamento},
        )
        if programacion_academica.estado != 'publicada':
            programacion_academica.estado = 'publicada'
            programacion_academica.save(update_fields=['estado'])

        grupo_prog2, _ = Grupo.objects.get_or_create(
            programacion_academica=programacion_academica,
            asignatura=prog2,
            nombre='A',
            defaults={'cupo_maximo': 25, 'cupo_disponible': 25, 'docente': docente},
        )
        HorarioGrupo.objects.get_or_create(
            grupo=grupo_prog2, dia_semana='lunes',
            hora_inicio=time(8, 0), hora_fin=time(10, 0),
            defaults={'salon': salon},
        )

        # Grupo de Cálculo II (para probar el rechazo por prerrequisito faltante)
        grupo_calculo2, _ = Grupo.objects.get_or_create(
            programacion_academica=programacion_academica,
            asignatura=calculo2,
            nombre='A',
            defaults={'cupo_maximo': 25, 'cupo_disponible': 25, 'docente': docente},
        )
        HorarioGrupo.objects.get_or_create(
            grupo=grupo_calculo2, dia_semana='martes',
            hora_inicio=time(10, 0), hora_fin=time(12, 0),
            defaults={'salon': salon},
        )

        # -----------------------------------------------------------------
        # 10) Periodo de matrícula vigente (publicado, hoy dentro de rango)
        # -----------------------------------------------------------------
        periodo_matricula, _ = PeriodoMatricula.objects.get_or_create(
            periodo_academico=periodo_academico,
            defaults={
                'fecha_inicio': hoy - timedelta(days=5),
                'fecha_fin': hoy + timedelta(days=10),
                'estado': 'publicado',
                'jefe_departamento': jefe_departamento,
            },
        )
        if periodo_matricula.estado != 'publicado':
            periodo_matricula.estado = 'publicado'
            periodo_matricula.save(update_fields=['estado'])

        # -----------------------------------------------------------------
        # 11) Requisitos documentales del periodo de matrícula
        #    (cantidad y tipo definidos libremente por el Jefe de
        #    Departamento; estos son solo un ejemplo de prueba)
        # -----------------------------------------------------------------
        requisito_certificado, _ = RequisitoDocumental.objects.get_or_create(
            periodo_matricula=periodo_matricula,
            nombre='Certificado de notas',
            defaults={
                'descripcion': 'Certificado de notas del último período cursado.',
                'formato': 'PDF',
            },
        )
        requisito_identidad, _ = RequisitoDocumental.objects.get_or_create(
            periodo_matricula=periodo_matricula,
            nombre='Documento de identidad',
            defaults={
                'descripcion': 'Copia del documento de identidad legible por ambas caras.',
                'formato': 'PDF/JPG',
            },
        )
        requisito_recibo, _ = RequisitoDocumental.objects.get_or_create(
            periodo_matricula=periodo_matricula,
            nombre='Recibo de pago de matrícula financiera',
            defaults={
                'descripcion': 'Comprobante de pago de la matrícula financiera del periodo.',
                'formato': 'PDF',
            },
        )

        self.stdout.write(self.style.SUCCESS('\n=== Datos de prueba listos ==='))
        self.stdout.write(f'Estudiante: {estudiante.codigo} (usuario: {estudiante.usuario.correo})')
        self.stdout.write(f'Jefe de Departamento: {jefe_departamento.codigo} (usuario: {usuario_jefe.correo} / Jefe12345)')
        self.stdout.write(f'Grupo disponible para matricular: {grupo_prog2} (id={grupo_prog2.id}), cupo {grupo_prog2.cupo_disponible}')
        self.stdout.write(f'Grupo SIN prerrequisito cumplido (para prueba de rechazo): {grupo_calculo2} (id={grupo_calculo2.id})')
        self.stdout.write(f'Periodo de matrícula id={periodo_matricula.id} (vigente hasta {periodo_matricula.fecha_fin})')
        self.stdout.write(
            f'Requisitos documentales creados: {requisito_certificado.id}, '
            f'{requisito_identidad.id}, {requisito_recibo.id}'
        )