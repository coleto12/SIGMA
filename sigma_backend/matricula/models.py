"""
Modelos del bloque Matrícula Académica.
Representa: PeriodoMatricula, RequisitoDocumental, SolicitudMatricula,
SolicitudAsignatura, DocumentoAdjunto, MatriculaOficial.

Decisión de diseño (ver notas del proyecto - flujo de resubmisión):
cada nuevo intento de matrícula en un periodo crea un nuevo registro de
SolicitudMatricula (campo num_intento) en lugar de sobrescribir el anterior.
SolicitudAsignatura y DocumentoAdjunto heredan este patrón a través de su FK
hacia SolicitudMatricula (on_delete=CASCADE), de modo que el historial de
intentos previos queda preservado salvo que se elimine la solicitud misma.
"""
from django.db import models
from usuarios.models import Estudiante, JefeDepartamento
from academico.models import PeriodoAcademico
from programacion.models import Grupo


class PeriodoMatricula(models.Model):
    ESTADO_CHOICES = [
        ('no_publicado', 'No publicado'),
        ('publicado', 'Publicado'),
    ]

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    periodo_academico = models.ForeignKey(
        PeriodoAcademico,
        on_delete=models.PROTECT,
        related_name='periodos_matricula',
    )
    jefe_departamento = models.ForeignKey(
        JefeDepartamento,
        on_delete=models.PROTECT,
        related_name='periodos_matricula',
    )

    class Meta:
        verbose_name = 'Periodo de Matrícula'
        verbose_name_plural = 'Periodos de Matrícula'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'Matrícula {self.periodo_academico.nombre} ({self.estado})'


class RequisitoDocumental(models.Model):
    FORMATO_CHOICES = [
        ('PDF', 'PDF'),
        ('JPG', 'JPG'),
        ('PDF/JPG', 'PDF/JPG'),
    ]

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(null=True, blank=True)
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES)
    periodo_matricula = models.ForeignKey(
        PeriodoMatricula,
        on_delete=models.PROTECT,
        related_name='requisitos_documentales',
    )

    class Meta:
        verbose_name = 'Requisito Documental'
        verbose_name_plural = 'Requisitos Documentales'
        ordering = ['periodo_matricula', 'nombre']

    def __str__(self):
        return self.nombre


class SolicitudMatricula(models.Model):
    ESTADO_CHOICES = [
        ('pendiente_revision', 'Pendiente de revisión'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    num_intento = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    motivo_rechazo = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.PROTECT,
        related_name='solicitudes_matricula',
    )
    periodo_matricula = models.ForeignKey(
        PeriodoMatricula,
        on_delete=models.PROTECT,
        related_name='solicitudes_matricula',
    )

    class Meta:
        verbose_name = 'Solicitud de Matrícula'
        verbose_name_plural = 'Solicitudes de Matrícula'
        ordering = ['-created_at']

    def __str__(self):
        return f'Solicitud #{self.pk} - {self.estudiante.codigo} ({self.estado})'


class SolicitudAsignatura(models.Model):
    solicitud_matricula = models.ForeignKey(
        SolicitudMatricula,
        on_delete=models.CASCADE,
        related_name='asignaturas_solicitadas',
    )
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.PROTECT,
        related_name='solicitudes_asignatura',
    )

    class Meta:
        verbose_name = 'Asignatura Solicitada'
        verbose_name_plural = 'Asignaturas Solicitadas'
        constraints = [
            models.UniqueConstraint(
                fields=['solicitud_matricula', 'grupo'],
                name='uk_solicitud_grupo',
            )
        ]

    def __str__(self):
        return f'{self.solicitud_matricula} - {self.grupo}'


def ruta_documento_adjunto(instance, filename):
    """Organiza los documentos adjuntos por estudiante y solicitud."""
    solicitud = instance.solicitud_matricula
    return f'documentos_adjuntos/estudiante_{solicitud.estudiante_id}/solicitud_{solicitud.pk}/{filename}'


class DocumentoAdjunto(models.Model):
    nombre_archivo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to=ruta_documento_adjunto, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField(default=1)
    solicitud_matricula = models.ForeignKey(
        SolicitudMatricula,
        on_delete=models.CASCADE,
        related_name='documentos_adjuntos',
    )
    requisito_documental = models.ForeignKey(
        RequisitoDocumental,
        on_delete=models.PROTECT,
        related_name='documentos_adjuntos',
    )

    class Meta:
        verbose_name = 'Documento Adjunto'
        verbose_name_plural = 'Documentos Adjuntos'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.nombre_archivo} (v{self.version})'


def ruta_matricula_oficial(instance, filename):
    return f'matriculas_oficiales/{instance.solicitud_matricula.estudiante_id}/{filename}'


class MatriculaOficial(models.Model):
    documento = models.FileField(upload_to=ruta_matricula_oficial, max_length=500)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    solicitud_matricula = models.OneToOneField(
        SolicitudMatricula,
        on_delete=models.PROTECT,
        related_name='matricula_oficial',
    )
    jefe_departamento = models.ForeignKey(
        JefeDepartamento,
        on_delete=models.PROTECT,
        related_name='matriculas_oficiales_generadas',
    )

    class Meta:
        verbose_name = 'Matrícula Oficial'
        verbose_name_plural = 'Matrículas Oficiales'
        ordering = ['-fecha_emision']

    def __str__(self):
        return f'Matrícula Oficial - {self.solicitud_matricula.estudiante.codigo}'
