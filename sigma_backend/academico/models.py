"""
Modelos del bloque Académico.
Representa: PeriodoAcademico, PlanEstudio, Asignatura, PlanEstudioAsignatura,
Prerrequisito, HistorialAcademico.

Decisiones de diseño relevantes (ver notas del proyecto):
- PlanEstudioAsignatura es la tabla intermedia que sí se necesita (a diferencia
  de un "plan_asignatura" generico que se descarto): aqui viven creditos y
  semestre porque ambos dependen de la combinacion plan+asignatura, no de la
  asignatura por si sola (la misma asignatura puede tener distintos creditos
  o ubicarse en distinto semestre segun el plan de estudio).
- Prerrequisito es una relacion reflexiva M2M sobre Asignatura.
- HistorialAcademico usa un ENUM (estado) en lugar de booleano, para soportar
  el estado 'en_curso' ademas de aprobada/reprobada.
"""
from django.db import models
from institucional.models import ProgramaAcademico
from usuarios.models import Estudiante


class PeriodoAcademico(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('cerrado', 'Cerrado'),
    ]

    nombre = models.CharField(max_length=20, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)

    class Meta:
        verbose_name = 'Periodo Académico'
        verbose_name_plural = 'Periodos Académicos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.nombre


class PlanEstudio(models.Model):
    ESTADO_CHOICES = [
        ('vigente', 'Vigente'),
        ('no_vigente', 'No vigente'),
    ]

    nombre = models.CharField(max_length=125)
    version = models.CharField(max_length=20)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    programa_academico = models.ForeignKey(
        ProgramaAcademico,
        on_delete=models.PROTECT,
        related_name='planes_estudio',
    )

    class Meta:
        verbose_name = 'Plan de Estudio'
        verbose_name_plural = 'Planes de Estudio'
        ordering = ['programa_academico', '-version']

    def __str__(self):
        return f'{self.nombre} (v{self.version})'


class Asignatura(models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=25, unique=True)

    class Meta:
        verbose_name = 'Asignatura'
        verbose_name_plural = 'Asignaturas'
        ordering = ['codigo']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class PlanEstudioAsignatura(models.Model):
    plan_estudio = models.ForeignKey(
        PlanEstudio,
        on_delete=models.CASCADE,
        related_name='asignaturas_plan',
    )
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='planes_asignatura',
    )
    creditos = models.PositiveIntegerField()
    semestre = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Asignatura del Plan de Estudio'
        verbose_name_plural = 'Asignaturas del Plan de Estudio'
        constraints = [
            models.UniqueConstraint(
                fields=['plan_estudio', 'asignatura'],
                name='uk_plan_asignatura',
            )
        ]
        ordering = ['plan_estudio', 'semestre']

    def __str__(self):
        return f'{self.asignatura.codigo} en {self.plan_estudio} (sem. {self.semestre})'


class Prerrequisito(models.Model):
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='prerrequisitos',
        help_text='Asignatura que exige el prerrequisito',
    )
    asignatura_prerrequisito = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='es_prerrequisito_de',
        help_text='Asignatura que debe haberse aprobado antes',
    )

    class Meta:
        verbose_name = 'Prerrequisito'
        verbose_name_plural = 'Prerrequisitos'
        constraints = [
            models.UniqueConstraint(
                fields=['asignatura', 'asignatura_prerrequisito'],
                name='uk_asignatura_prerrequisito',
            )
        ]

    def __str__(self):
        return f'{self.asignatura_prerrequisito.codigo} es prerrequisito de {self.asignatura.codigo}'


class HistorialAcademico(models.Model):
    ESTADO_CHOICES = [
        ('aprobada', 'Aprobada'),
        ('reprobada', 'Reprobada'),
        ('en_curso', 'En curso'),
    ]

    nota = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.PROTECT,
        related_name='historial_academico',
    )
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.PROTECT,
        related_name='historial_academico',
    )
    periodo_academico = models.ForeignKey(
        PeriodoAcademico,
        on_delete=models.PROTECT,
        related_name='historial_academico',
    )

    class Meta:
        verbose_name = 'Historial Académico'
        verbose_name_plural = 'Historiales Académicos'
        constraints = [
            models.UniqueConstraint(
                fields=['estudiante', 'asignatura', 'periodo_academico'],
                name='uk_historial_estudiante_asignatura_periodo',
            )
        ]
        ordering = ['-periodo_academico', 'estudiante']

    def __str__(self):
        return f'{self.estudiante.codigo} - {self.asignatura.codigo} ({self.estado})'
