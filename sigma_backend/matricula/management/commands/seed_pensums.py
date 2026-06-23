"""
Comando de management para poblar planes de estudio (pensums) de prueba
para 9 programas académicos de la Universidad de Cartagena.

Uso:
    python manage.py seed_pensums

Es idempotente: usa bulk_create con ignore_conflicts=True, así que se
puede correr varias veces sin duplicar registros. Usa inserciones en
lote (en vez de un get_or_create por fila) para minimizar el número de
viajes de red hacia la base de datos remota (Supabase), ya que el
enfoque anterior con cientos de consultas individuales resultaba
extremadamente lento.

Nota interna (no se expone en la interfaz): las mallas curriculares aquí
son genéricas y representativas de la estructura típica de estos programas
en universidades colombianas (semestres, progresión básica -> profesional,
prerrequisitos lógicos). No corresponden a documentos oficiales descargados
de la Universidad de Cartagena, ya que no se logró acceso automatizado a
las páginas oficiales (bloqueadas para scraping). Sirven como datos de
prueba realistas para demostrar el funcionamiento de PlanEstudio,
PlanEstudioAsignatura y Prerrequisito.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from institucional.models import Campus, Facultad, NivelFormacion, ProgramaAcademico
from academico.models import PlanEstudio, Asignatura, PlanEstudioAsignatura, Prerrequisito


class Command(BaseCommand):
    help = 'Crea planes de estudio (pensums) de prueba para 9 programas académicos.'

    @transaction.atomic
    def handle(self, *args, **options):
        campus, _ = Campus.objects.get_or_create(
            nombre='Piedra de Bolívar',
            defaults={'direccion': 'Cartagena de Indias'},
        )
        nivel_pregrado, _ = NivelFormacion.objects.get_or_create(nombre='Pregrado')

        # -------------------------------------------------------------
        # Facultades (solo 5 filas, get_or_create individual está bien aquí)
        # -------------------------------------------------------------
        fac_ingenieria, _ = Facultad.objects.get_or_create(nombre='Ingeniería', defaults={'campus': campus})
        fac_medicina, _ = Facultad.objects.get_or_create(nombre='Medicina', defaults={'campus': campus})
        fac_enfermeria, _ = Facultad.objects.get_or_create(nombre='Enfermería', defaults={'campus': campus})
        fac_odontologia, _ = Facultad.objects.get_or_create(nombre='Odontología', defaults={'campus': campus})
        fac_ciencias, _ = Facultad.objects.get_or_create(nombre='Ciencias Exactas y Naturales', defaults={'campus': campus})

        # -------------------------------------------------------------
        # Programas académicos (9 filas, get_or_create individual está bien)
        # -------------------------------------------------------------
        programa_sistemas, _ = ProgramaAcademico.objects.get_or_create(
            codigo='ISIS', defaults={'nombre': 'Ingeniería de Sistemas', 'facultad': fac_ingenieria, 'nivel_formacion': nivel_pregrado},
        )
        programa_civil, _ = ProgramaAcademico.objects.get_or_create(
            codigo='ICIV', defaults={'nombre': 'Ingeniería Civil', 'facultad': fac_ingenieria, 'nivel_formacion': nivel_pregrado},
        )
        programa_alimentos, _ = ProgramaAcademico.objects.get_or_create(
            codigo='IALI', defaults={'nombre': 'Ingeniería de Alimentos', 'facultad': fac_ingenieria, 'nivel_formacion': nivel_pregrado},
        )
        programa_quimica, _ = ProgramaAcademico.objects.get_or_create(
            codigo='IQUI', defaults={'nombre': 'Ingeniería Química', 'facultad': fac_ingenieria, 'nivel_formacion': nivel_pregrado},
        )
        programa_medicina, _ = ProgramaAcademico.objects.get_or_create(
            codigo='MED', defaults={'nombre': 'Medicina', 'facultad': fac_medicina, 'nivel_formacion': nivel_pregrado},
        )
        programa_enfermeria, _ = ProgramaAcademico.objects.get_or_create(
            codigo='ENF', defaults={'nombre': 'Enfermería', 'facultad': fac_enfermeria, 'nivel_formacion': nivel_pregrado},
        )
        programa_odontologia, _ = ProgramaAcademico.objects.get_or_create(
            codigo='ODO', defaults={'nombre': 'Odontología', 'facultad': fac_odontologia, 'nivel_formacion': nivel_pregrado},
        )
        programa_matematicas, _ = ProgramaAcademico.objects.get_or_create(
            codigo='MAT', defaults={'nombre': 'Matemáticas', 'facultad': fac_ciencias, 'nivel_formacion': nivel_pregrado},
        )
        programa_fisica, _ = ProgramaAcademico.objects.get_or_create(
            codigo='FIS', defaults={'nombre': 'Física', 'facultad': fac_ciencias, 'nivel_formacion': nivel_pregrado},
        )

        # -------------------------------------------------------------
        # 1) Crear los 9 PlanEstudio (1 consulta por programa, get_or_create
        #    está bien aquí porque son solo 9 filas).
        # -------------------------------------------------------------
        planes = {}
        for programa, nombre_plan in [
            (programa_sistemas, 'Ingeniería de Sistemas'),
            (programa_civil, 'Ingeniería Civil'),
            (programa_alimentos, 'Ingeniería de Alimentos'),
            (programa_quimica, 'Ingeniería Química'),
            (programa_medicina, 'Medicina'),
            (programa_enfermeria, 'Enfermería'),
            (programa_odontologia, 'Odontología'),
            (programa_matematicas, 'Matemáticas'),
            (programa_fisica, 'Física'),
        ]:
            plan, _ = PlanEstudio.objects.get_or_create(
                programa_academico=programa, version='1',
                defaults={'nombre': nombre_plan, 'estado': 'vigente'},
            )
            planes[programa.codigo] = plan

        # -------------------------------------------------------------
        # 2) Definir TODA la malla de los 9 programas en memoria primero
        # -------------------------------------------------------------
        mapas = {
            'ISIS': self._mapa_sistemas(),
            'ICIV': self._mapa_civil(),
            'IALI': self._mapa_alimentos(),
            'IQUI': self._mapa_quimica(),
            'MED': self._mapa_medicina(),
            'ENF': self._mapa_enfermeria(),
            'ODO': self._mapa_odontologia(),
            'MAT': self._mapa_matematicas(),
            'FIS': self._mapa_fisica(),
        }
        prerrequisitos_por_programa = {
            'ISIS': self._prereqs_sistemas(),
            'ICIV': self._prereqs_civil(),
            'IALI': self._prereqs_alimentos(),
            'IQUI': self._prereqs_quimica(),
            'MED': self._prereqs_medicina(),
            'ENF': self._prereqs_enfermeria(),
            'ODO': self._prereqs_odontologia(),
            'MAT': self._prereqs_matematicas(),
            'FIS': self._prereqs_fisica(),
        }

        # -------------------------------------------------------------
        # 3) Insertar TODAS las asignaturas de los 9 programas en UN
        #    SOLO bulk_create (1 viaje de red en vez de ~287).
        # -------------------------------------------------------------
        asignaturas_a_crear = []
        codigos_vistos = set()
        for mapa in mapas.values():
            for _, lista in mapa.items():
                for codigo, nombre, _creditos in lista:
                    if codigo not in codigos_vistos:
                        asignaturas_a_crear.append(Asignatura(codigo=codigo, nombre=nombre))
                        codigos_vistos.add(codigo)

        Asignatura.objects.bulk_create(asignaturas_a_crear, ignore_conflicts=True)

        # Traer TODAS las asignaturas de una vez (1 consulta) y armar el
        # diccionario código -> instancia, para usarlo al crear las demás
        # tablas sin volver a golpear la base de datos por cada una.
        todas_asignaturas = {a.codigo: a for a in Asignatura.objects.filter(codigo__in=codigos_vistos)}

        # -------------------------------------------------------------
        # 4) Insertar TODAS las filas de PlanEstudioAsignatura en bloque
        # -------------------------------------------------------------
        filas_plan_asignatura = []
        for codigo_programa, mapa in mapas.items():
            plan = planes[codigo_programa]
            for semestre, lista in mapa.items():
                for codigo, _nombre, creditos in lista:
                    filas_plan_asignatura.append(PlanEstudioAsignatura(
                        plan_estudio=plan,
                        asignatura=todas_asignaturas[codigo],
                        creditos=creditos,
                        semestre=semestre,
                    ))
        PlanEstudioAsignatura.objects.bulk_create(filas_plan_asignatura, ignore_conflicts=True)

        # -------------------------------------------------------------
        # 5) Insertar TODOS los prerrequisitos en bloque
        # -------------------------------------------------------------
        filas_prerrequisito = []
        for codigo_programa, pares in prerrequisitos_por_programa.items():
            for codigo_asig, codigo_prereq in pares:
                filas_prerrequisito.append(Prerrequisito(
                    asignatura=todas_asignaturas[codigo_asig],
                    asignatura_prerrequisito=todas_asignaturas[codigo_prereq],
                ))
        Prerrequisito.objects.bulk_create(filas_prerrequisito, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('\n=== Pensums de prueba creados exitosamente ==='))
        self.stdout.write(f'Total de planes de estudio: {PlanEstudio.objects.count()}')
        self.stdout.write(f'Total de asignaturas: {Asignatura.objects.count()}')
        self.stdout.write(f'Total de filas plan-asignatura: {PlanEstudioAsignatura.objects.count()}')
        self.stdout.write(f'Total de prerrequisitos: {Prerrequisito.objects.count()}')

    # -----------------------------------------------------------------
    # Mapas de malla por programa: { semestre: [(codigo, nombre, creditos), ...] }
    # -----------------------------------------------------------------
    def _mapa_sistemas(self):
        return {
            1: [('ISIS-101', 'Programación I', 4), ('ISIS-103', 'Cálculo I', 4), ('ISIS-105', 'Álgebra Lineal', 3), ('ISIS-107', 'Cátedra Institucional', 2)],
            2: [('ISIS-102', 'Programación II', 4), ('ISIS-104', 'Cálculo II', 4), ('ISIS-106', 'Física I', 4), ('ISIS-108', 'Lógica Matemática', 3)],
            3: [('ISIS-201', 'Estructuras de Datos', 4), ('ISIS-203', 'Cálculo III', 4), ('ISIS-205', 'Física II', 4), ('ISIS-207', 'Estadística I', 3)],
            4: [('ISIS-202', 'Bases de Datos I', 4), ('ISIS-204', 'Arquitectura de Computadores', 3), ('ISIS-206', 'Métodos Numéricos', 3), ('ISIS-208', 'Investigación de Operaciones', 3)],
            5: [('ISIS-301', 'Bases de Datos II', 4), ('ISIS-303', 'Sistemas Operativos', 4), ('ISIS-305', 'Ingeniería de Software I', 4), ('ISIS-307', 'Redes de Computadores', 3)],
            6: [('ISIS-302', 'Ingeniería de Software II', 4), ('ISIS-304', 'Inteligencia Artificial', 3), ('ISIS-306', 'Seguridad Informática', 3), ('ISIS-308', 'Sistemas Distribuidos', 3)],
            7: [('ISIS-401', 'Desarrollo Web', 3), ('ISIS-403', 'Desarrollo Móvil', 3), ('ISIS-405', 'Gestión de Proyectos de TI', 3), ('ISIS-407', 'Electiva Profesional I', 3)],
            8: [('ISIS-402', 'Auditoría de Sistemas', 3), ('ISIS-404', 'Electiva Profesional II', 3), ('ISIS-406', 'Formulación de Proyectos', 3), ('ISIS-408', 'Práctica Profesional', 6)],
        }

    def _prereqs_sistemas(self):
        return [
            ('ISIS-102', 'ISIS-101'), ('ISIS-104', 'ISIS-103'), ('ISIS-201', 'ISIS-102'),
            ('ISIS-203', 'ISIS-104'), ('ISIS-205', 'ISIS-106'), ('ISIS-202', 'ISIS-201'),
            ('ISIS-301', 'ISIS-202'), ('ISIS-303', 'ISIS-204'), ('ISIS-305', 'ISIS-201'),
            ('ISIS-302', 'ISIS-305'), ('ISIS-401', 'ISIS-301'), ('ISIS-403', 'ISIS-401'),
        ]

    def _mapa_civil(self):
        return {
            1: [('ICIV-101', 'Cálculo I', 4), ('ICIV-103', 'Álgebra Lineal', 3), ('ICIV-105', 'Química General', 3), ('ICIV-107', 'Dibujo de Ingeniería', 2)],
            2: [('ICIV-102', 'Cálculo II', 4), ('ICIV-104', 'Física I', 4), ('ICIV-106', 'Geología', 3), ('ICIV-108', 'Programación Básica', 3)],
            3: [('ICIV-201', 'Cálculo III', 4), ('ICIV-203', 'Física II', 4), ('ICIV-205', 'Estática', 3), ('ICIV-207', 'Topografía', 3)],
            4: [('ICIV-202', 'Ecuaciones Diferenciales', 3), ('ICIV-204', 'Mecánica de Materiales', 4), ('ICIV-206', 'Probabilidad y Estadística', 3), ('ICIV-208', 'Hidráulica Básica', 3)],
            5: [('ICIV-301', 'Mecánica de Suelos', 4), ('ICIV-303', 'Análisis Estructural I', 4), ('ICIV-305', 'Materiales de Construcción', 3), ('ICIV-307', 'Hidrología', 3)],
            6: [('ICIV-302', 'Análisis Estructural II', 4), ('ICIV-304', 'Diseño de Pavimentos', 3), ('ICIV-306', 'Acueductos y Alcantarillados', 3), ('ICIV-308', 'Cimentaciones', 3)],
            7: [('ICIV-401', 'Diseño en Concreto', 4), ('ICIV-403', 'Vías I', 3), ('ICIV-405', 'Gerencia de Proyectos', 3), ('ICIV-407', 'Electiva I', 3)],
            8: [('ICIV-402', 'Diseño en Acero', 3), ('ICIV-404', 'Vías II', 3), ('ICIV-406', 'Formulación de Proyectos', 3), ('ICIV-408', 'Práctica Profesional', 6)],
        }

    def _prereqs_civil(self):
        return [
            ('ICIV-102', 'ICIV-101'), ('ICIV-104', 'ICIV-103'), ('ICIV-201', 'ICIV-102'),
            ('ICIV-203', 'ICIV-104'), ('ICIV-204', 'ICIV-205'), ('ICIV-301', 'ICIV-206'),
            ('ICIV-303', 'ICIV-204'), ('ICIV-302', 'ICIV-303'), ('ICIV-401', 'ICIV-302'),
            ('ICIV-402', 'ICIV-401'),
        ]

    def _mapa_alimentos(self):
        return {
            1: [('IALI-101', 'Cálculo I', 4), ('IALI-103', 'Química General', 4), ('IALI-105', 'Biología', 3), ('IALI-107', 'Introducción a la Ingeniería', 2)],
            2: [('IALI-102', 'Cálculo II', 4), ('IALI-104', 'Química Orgánica', 4), ('IALI-106', 'Física I', 4), ('IALI-108', 'Microbiología General', 3)],
            3: [('IALI-201', 'Fisicoquímica', 4), ('IALI-203', 'Bioquímica de Alimentos', 4), ('IALI-205', 'Estadística', 3), ('IALI-207', 'Balance de Materia y Energía', 4)],
            4: [('IALI-202', 'Microbiología de Alimentos', 4), ('IALI-204', 'Operaciones Unitarias I', 4), ('IALI-206', 'Análisis de Alimentos', 3), ('IALI-208', 'Termodinámica', 3)],
            5: [('IALI-301', 'Operaciones Unitarias II', 4), ('IALI-303', 'Tecnología de Cereales', 3), ('IALI-305', 'Empaques y Envases', 3), ('IALI-307', 'Control de Calidad', 3)],
            6: [('IALI-302', 'Tecnología de Lácteos', 3), ('IALI-304', 'Tecnología de Carnes', 3), ('IALI-306', 'Ingeniería de Procesos', 4), ('IALI-308', 'Legislación Alimentaria', 2)],
            7: [('IALI-401', 'Diseño de Plantas', 4), ('IALI-403', 'Gestión de Calidad y BPM', 3), ('IALI-405', 'Nutrición', 3), ('IALI-407', 'Electiva I', 3)],
            8: [('IALI-402', 'Desarrollo de Nuevos Productos', 3), ('IALI-404', 'Formulación de Proyectos', 3), ('IALI-406', 'Gestión Ambiental', 3), ('IALI-408', 'Práctica Profesional', 6)],
        }

    def _prereqs_alimentos(self):
        return [
            ('IALI-102', 'IALI-101'), ('IALI-104', 'IALI-103'), ('IALI-201', 'IALI-104'),
            ('IALI-203', 'IALI-104'), ('IALI-202', 'IALI-108'), ('IALI-204', 'IALI-207'),
            ('IALI-301', 'IALI-204'), ('IALI-302', 'IALI-301'), ('IALI-401', 'IALI-306'),
        ]

    def _mapa_quimica(self):
        return {
            1: [('IQUI-101', 'Cálculo I', 4), ('IQUI-103', 'Química General', 4), ('IQUI-105', 'Álgebra Lineal', 3), ('IQUI-107', 'Introducción a la Ingeniería Química', 2)],
            2: [('IQUI-102', 'Cálculo II', 4), ('IQUI-104', 'Química Orgánica I', 4), ('IQUI-106', 'Física I', 4), ('IQUI-108', 'Química Inorgánica', 3)],
            3: [('IQUI-201', 'Cálculo III', 4), ('IQUI-203', 'Química Orgánica II', 4), ('IQUI-205', 'Física II', 4), ('IQUI-207', 'Balance de Materia', 4)],
            4: [('IQUI-202', 'Ecuaciones Diferenciales', 3), ('IQUI-204', 'Fisicoquímica I', 4), ('IQUI-206', 'Balance de Energía', 4), ('IQUI-208', 'Análisis Químico', 3)],
            5: [('IQUI-301', 'Fisicoquímica II', 4), ('IQUI-303', 'Operaciones Unitarias I', 4), ('IQUI-305', 'Termodinámica del Equilibrio', 4), ('IQUI-307', 'Estadística', 3)],
            6: [('IQUI-302', 'Operaciones Unitarias II', 4), ('IQUI-304', 'Fenómenos de Transporte', 4), ('IQUI-306', 'Cinética y Catálisis', 3), ('IQUI-308', 'Control de Procesos', 3)],
            7: [('IQUI-401', 'Diseño de Reactores', 4), ('IQUI-403', 'Diseño de Plantas Químicas', 4), ('IQUI-405', 'Seguridad Industrial', 3), ('IQUI-407', 'Electiva I', 3)],
            8: [('IQUI-402', 'Simulación de Procesos', 3), ('IQUI-404', 'Gestión Ambiental', 3), ('IQUI-406', 'Formulación de Proyectos', 3), ('IQUI-408', 'Práctica Profesional', 6)],
        }

    def _prereqs_quimica(self):
        return [
            ('IQUI-102', 'IQUI-101'), ('IQUI-104', 'IQUI-103'), ('IQUI-203', 'IQUI-104'),
            ('IQUI-204', 'IQUI-205'), ('IQUI-207', 'IQUI-102'), ('IQUI-301', 'IQUI-204'),
            ('IQUI-303', 'IQUI-207'), ('IQUI-302', 'IQUI-303'), ('IQUI-401', 'IQUI-306'),
            ('IQUI-403', 'IQUI-302'),
        ]

    def _mapa_medicina(self):
        return {
            1: [('MED-101', 'Biología Celular', 4), ('MED-103', 'Química General', 4), ('MED-105', 'Anatomía I', 4), ('MED-107', 'Introducción a la Medicina', 2)],
            2: [('MED-102', 'Histología', 4), ('MED-104', 'Bioquímica I', 4), ('MED-106', 'Anatomía II', 4), ('MED-108', 'Embriología', 3)],
            3: [('MED-201', 'Fisiología I', 4), ('MED-203', 'Bioquímica II', 4), ('MED-205', 'Microbiología', 4), ('MED-207', 'Genética', 3)],
            4: [('MED-202', 'Fisiología II', 4), ('MED-204', 'Inmunología', 3), ('MED-206', 'Parasitología', 3), ('MED-208', 'Farmacología I', 4)],
            5: [('MED-301', 'Patología General', 4), ('MED-303', 'Farmacología II', 4), ('MED-305', 'Semiología', 4), ('MED-307', 'Epidemiología', 3)],
            6: [('MED-302', 'Patología Sistémica', 4), ('MED-304', 'Medicina Interna I', 4), ('MED-306', 'Cirugía I', 4), ('MED-308', 'Salud Pública', 3)],
            7: [('MED-401', 'Medicina Interna II', 4), ('MED-403', 'Cirugía II', 4), ('MED-405', 'Pediatría I', 4), ('MED-407', 'Ginecobstetricia I', 4)],
            8: [('MED-402', 'Pediatría II', 4), ('MED-404', 'Ginecobstetricia II', 4), ('MED-406', 'Psiquiatría', 3), ('MED-408', 'Medicina Familiar', 3)],
        }

    def _prereqs_medicina(self):
        return [
            ('MED-102', 'MED-101'), ('MED-104', 'MED-103'), ('MED-201', 'MED-105'),
            ('MED-203', 'MED-104'), ('MED-202', 'MED-201'), ('MED-208', 'MED-203'),
            ('MED-301', 'MED-102'), ('MED-303', 'MED-208'), ('MED-305', 'MED-202'),
            ('MED-302', 'MED-301'), ('MED-304', 'MED-305'), ('MED-401', 'MED-304'),
        ]

    def _mapa_enfermeria(self):
        return {
            1: [('ENF-101', 'Biología Celular', 3), ('ENF-103', 'Anatomía', 4), ('ENF-105', 'Fundamentos de Enfermería I', 4), ('ENF-107', 'Psicología General', 2)],
            2: [('ENF-102', 'Fisiología', 4), ('ENF-104', 'Bioquímica', 3), ('ENF-106', 'Fundamentos de Enfermería II', 4), ('ENF-108', 'Nutrición', 3)],
            3: [('ENF-201', 'Farmacología', 4), ('ENF-203', 'Microbiología', 3), ('ENF-205', 'Enfermería del Adulto I', 4), ('ENF-207', 'Bioética', 2)],
            4: [('ENF-202', 'Patología', 3), ('ENF-204', 'Enfermería del Adulto II', 4), ('ENF-206', 'Enfermería Materno Infantil I', 4), ('ENF-208', 'Epidemiología', 3)],
            5: [('ENF-301', 'Enfermería Materno Infantil II', 4), ('ENF-303', 'Enfermería en Salud Mental', 3), ('ENF-305', 'Enfermería Comunitaria I', 4), ('ENF-307', 'Bioestadística', 3)],
            6: [('ENF-302', 'Enfermería en Cuidado Crítico', 4), ('ENF-304', 'Enfermería Comunitaria II', 4), ('ENF-306', 'Gerencia en Enfermería', 3), ('ENF-308', 'Investigación en Salud', 3)],
            7: [('ENF-401', 'Enfermería Pediátrica', 4), ('ENF-403', 'Enfermería Quirúrgica', 4), ('ENF-405', 'Salud Ocupacional', 3), ('ENF-407', 'Electiva I', 3)],
            8: [('ENF-402', 'Práctica Profesional I', 6), ('ENF-404', 'Práctica Profesional II', 6), ('ENF-406', 'Formulación de Proyectos', 2)],
        }

    def _prereqs_enfermeria(self):
        return [
            ('ENF-102', 'ENF-101'), ('ENF-106', 'ENF-105'), ('ENF-201', 'ENF-104'),
            ('ENF-205', 'ENF-106'), ('ENF-202', 'ENF-102'), ('ENF-204', 'ENF-205'),
            ('ENF-206', 'ENF-204'), ('ENF-301', 'ENF-206'), ('ENF-302', 'ENF-204'),
            ('ENF-401', 'ENF-301'),
        ]

    def _mapa_odontologia(self):
        return {
            1: [('ODO-101', 'Biología Celular', 3), ('ODO-103', 'Anatomía General', 4), ('ODO-105', 'Química General', 3), ('ODO-107', 'Introducción a la Odontología', 2)],
            2: [('ODO-102', 'Histología', 3), ('ODO-104', 'Anatomía Dental', 4), ('ODO-106', 'Bioquímica', 3), ('ODO-108', 'Embriología', 3)],
            3: [('ODO-201', 'Fisiología', 4), ('ODO-203', 'Microbiología Oral', 3), ('ODO-205', 'Materiales Dentales I', 3), ('ODO-207', 'Oclusión', 3)],
            4: [('ODO-202', 'Patología General', 3), ('ODO-204', 'Materiales Dentales II', 3), ('ODO-206', 'Radiología Oral', 3), ('ODO-208', 'Farmacología', 4)],
            5: [('ODO-301', 'Operatoria Dental I', 4), ('ODO-303', 'Periodoncia I', 3), ('ODO-305', 'Endodoncia I', 3), ('ODO-307', 'Patología Oral', 3)],
            6: [('ODO-302', 'Operatoria Dental II', 4), ('ODO-304', 'Periodoncia II', 3), ('ODO-306', 'Endodoncia II', 3), ('ODO-308', 'Cirugía Oral I', 3)],
            7: [('ODO-401', 'Prótesis I', 4), ('ODO-403', 'Ortodoncia I', 3), ('ODO-405', 'Odontopediatría', 3), ('ODO-407', 'Cirugía Oral II', 3)],
            8: [('ODO-402', 'Prótesis II', 4), ('ODO-404', 'Práctica Clínica Integral', 6), ('ODO-406', 'Gerencia en Salud Oral', 2)],
        }

    def _prereqs_odontologia(self):
        return [
            ('ODO-102', 'ODO-101'), ('ODO-104', 'ODO-103'), ('ODO-201', 'ODO-102'),
            ('ODO-205', 'ODO-104'), ('ODO-301', 'ODO-205'), ('ODO-303', 'ODO-201'),
            ('ODO-305', 'ODO-301'), ('ODO-302', 'ODO-301'), ('ODO-401', 'ODO-302'),
            ('ODO-403', 'ODO-207'),
        ]

    def _mapa_matematicas(self):
        return {
            1: [('MAT-101', 'Cálculo I', 4), ('MAT-103', 'Geometría Vectorial', 3), ('MAT-105', 'Lógica y Conjuntos', 3), ('MAT-107', 'Introducción a las Matemáticas', 2)],
            2: [('MAT-102', 'Cálculo II', 4), ('MAT-104', 'Álgebra Lineal I', 3), ('MAT-106', 'Física I', 4), ('MAT-108', 'Programación I', 3)],
            3: [('MAT-201', 'Cálculo III', 4), ('MAT-203', 'Álgebra Lineal II', 3), ('MAT-205', 'Estructuras Algebraicas I', 3), ('MAT-207', 'Programación II', 3)],
            4: [('MAT-202', 'Ecuaciones Diferenciales I', 4), ('MAT-204', 'Análisis Real I', 4), ('MAT-206', 'Estructuras Algebraicas II', 3), ('MAT-208', 'Probabilidad', 3)],
            5: [('MAT-301', 'Análisis Real II', 4), ('MAT-303', 'Ecuaciones Diferenciales II', 3), ('MAT-305', 'Topología General', 3), ('MAT-307', 'Estadística', 3)],
            6: [('MAT-302', 'Variable Compleja', 3), ('MAT-304', 'Geometría Diferencial', 3), ('MAT-306', 'Análisis Numérico', 3), ('MAT-308', 'Investigación de Operaciones', 3)],
            7: [('MAT-401', 'Teoría de la Medida', 3), ('MAT-403', 'Ecuaciones Diferenciales Parciales', 3), ('MAT-405', 'Electiva I', 3), ('MAT-407', 'Seminario de Investigación I', 2)],
            8: [('MAT-402', 'Análisis Funcional', 3), ('MAT-404', 'Electiva II', 3), ('MAT-406', 'Seminario de Investigación II', 2), ('MAT-408', 'Trabajo de Grado', 4)],
        }

    def _prereqs_matematicas(self):
        return [
            ('MAT-102', 'MAT-101'), ('MAT-201', 'MAT-102'), ('MAT-203', 'MAT-104'),
            ('MAT-205', 'MAT-203'), ('MAT-202', 'MAT-201'), ('MAT-204', 'MAT-201'),
            ('MAT-301', 'MAT-204'), ('MAT-303', 'MAT-202'), ('MAT-302', 'MAT-301'),
            ('MAT-401', 'MAT-301'), ('MAT-402', 'MAT-401'),
        ]

    def _mapa_fisica(self):
        return {
            1: [('FIS-101', 'Cálculo I', 4), ('FIS-103', 'Física Mecánica', 4), ('FIS-105', 'Álgebra Lineal', 3), ('FIS-107', 'Introducción a la Física', 2)],
            2: [('FIS-102', 'Cálculo II', 4), ('FIS-104', 'Física de Campos', 4), ('FIS-106', 'Programación I', 3), ('FIS-108', 'Química General', 3)],
            3: [('FIS-201', 'Cálculo III', 4), ('FIS-203', 'Termodinámica', 3), ('FIS-205', 'Ecuaciones Diferenciales', 3), ('FIS-207', 'Laboratorio de Física I', 2)],
            4: [('FIS-202', 'Mecánica Clásica I', 4), ('FIS-204', 'Métodos Matemáticos I', 3), ('FIS-206', 'Óptica', 3), ('FIS-208', 'Laboratorio de Física II', 2)],
            5: [('FIS-301', 'Mecánica Clásica II', 3), ('FIS-303', 'Electromagnetismo I', 4), ('FIS-305', 'Métodos Matemáticos II', 3), ('FIS-307', 'Física Estadística', 3)],
            6: [('FIS-302', 'Electromagnetismo II', 4), ('FIS-304', 'Mecánica Cuántica I', 4), ('FIS-306', 'Física Computacional', 3), ('FIS-308', 'Física de la Materia Condensada', 3)],
            7: [('FIS-401', 'Mecánica Cuántica II', 4), ('FIS-403', 'Física Nuclear', 3), ('FIS-405', 'Relatividad', 3), ('FIS-407', 'Seminario de Investigación I', 2)],
            8: [('FIS-402', 'Electrónica', 3), ('FIS-404', 'Electiva de Profundización', 3), ('FIS-406', 'Seminario de Investigación II', 2), ('FIS-408', 'Trabajo de Grado', 4)],
        }

    def _prereqs_fisica(self):
        return [
            ('FIS-102', 'FIS-101'), ('FIS-104', 'FIS-103'), ('FIS-201', 'FIS-102'),
            ('FIS-202', 'FIS-201'), ('FIS-203', 'FIS-104'), ('FIS-301', 'FIS-202'),
            ('FIS-303', 'FIS-104'), ('FIS-302', 'FIS-303'), ('FIS-304', 'FIS-301'),
            ('FIS-401', 'FIS-304'),
        ]