"""
Modelos del bloque Programación Académica.
Representa: ProgramacionAcademica, Salon, Grupo, HorarioGrupo.

Decisión de diseño (ver notas del proyecto): Grupo usa una PK simple
(autoincremental) en lugar de una PK compuesta. La dependencia existencial
de Grupo respecto a ProgramacionAcademica se expresa via on_delete=CASCADE,
sin propagar complejidad de claves compuestas hacia HorarioGrupo y
SolicitudAsignatura (bloque matricula).
"""
from django.db import models
from institucional.models import ProgramaAcademico, Campus
from usuarios.models import JefeDepartamento, Docente
from academico.models import PeriodoAcademico, Asignatura


class ProgramacionAcademica(models.Model):
    ESTADO_CHOICES = [
        ('no_publicada', 'No publicada'),
        ('publicada', 'Publicada'),
    ]

    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    programa_academico = models.ForeignKey(
        ProgramaAcademico,
        on_delete=models.PROTECT,
        related_name='programaciones_academicas',
    )
    periodo_academico = models.ForeignKey(
        PeriodoAcademico,
        on_delete=models.PROTECT,
        related_name='programaciones_academicas',
    )
    jefe_departamento = models.ForeignKey(
        JefeDepartamento,
        on_delete=models.PROTECT,
        related_name='programaciones_academicas',
    )

    class Meta:
        verbose_name = 'Programación Académica'
        verbose_name_plural = 'Programaciones Académicas'
        constraints = [
            models.UniqueConstraint(
                fields=['programa_academico', 'periodo_academico'],
                name='uk_programa_periodo',
            )
        ]
        ordering = ['-periodo_academico']

    def __str__(self):
        return f'{self.programa_academico.codigo} - {self.periodo_academico.nombre} ({self.estado})'


class Salon(models.Model):
    nombre = models.CharField(max_length=50)
    capacidad = models.PositiveIntegerField()
    campus = models.ForeignKey(
        Campus,
        on_delete=models.PROTECT,
        related_name='salones',
    )

    class Meta:
        verbose_name = 'Salón'
        verbose_name_plural = 'Salones'
        ordering = ['campus', 'nombre']

    def __str__(self):
        return f'{self.nombre} ({self.campus.nombre})'


class Grupo(models.Model):
    nombre = models.CharField(max_length=20)
    cupo_maximo = models.PositiveIntegerField()
    cupo_disponible = models.PositiveIntegerField()
    programacion_academica = models.ForeignKey(
        ProgramacionAcademica,
        on_delete=models.CASCADE,
        related_name='grupos',
    )
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.PROTECT,
        related_name='grupos',
    )
    docente = models.ForeignKey(
        Docente,
        on_delete=models.PROTECT,
        related_name='grupos',
    )

    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        constraints = [
            models.UniqueConstraint(
                fields=['programacion_academica', 'asignatura', 'nombre'],
                name='uk_programacion_asignatura_grupo',
            )
        ]
        ordering = ['asignatura', 'nombre']

    def __str__(self):
        return f'{self.asignatura.codigo} - Grupo {self.nombre}'


class HorarioGrupo(models.Model):
    DIA_SEMANA_CHOICES = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
    ]

    dia_semana = models.CharField(max_length=10, choices=DIA_SEMANA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.CASCADE,
        related_name='horarios',
    )
    salon = models.ForeignKey(
        Salon,
        on_delete=models.PROTECT,
        related_name='horarios',
    )

    class Meta:
        verbose_name = 'Horario de Grupo'
        verbose_name_plural = 'Horarios de Grupo'
        constraints = [
            models.UniqueConstraint(
                fields=['grupo', 'dia_semana', 'hora_inicio', 'hora_fin'],
                name='uk_horario_grupo',
            )
        ]
        ordering = ['dia_semana', 'hora_inicio']

    def __str__(self):
        return f'{self.grupo} - {self.dia_semana} {self.hora_inicio}-{self.hora_fin}'
