"""
Modelo del bloque Notificaciones.

Decisión de diseño (ver notas del proyecto): las notificaciones se persisten
como tabla en base de datos (no se manejan únicamente en código de
aplicación), para permitir historial, marcado de leído/no leído y consulta
posterior por parte del usuario.

Nota de migración MySQL -> Postgres: el campo 'leida' usaba TINYINT en el
script original; aquí se modela como BooleanField nativo, que es el tipo
correcto y resuelve ese issue pendiente.
"""
from django.db import models
from usuarios.models import Usuario


class Notificacion(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('solicitud_recibida', 'Solicitud recibida'),
        ('solicitud_aprobada', 'Solicitud aprobada'),
        ('solicitud_rechazada', 'Solicitud rechazada'),
        ('matricula_generada', 'Matrícula generada'),
        ('fecha_limite_proxima', 'Fecha límite próxima'),
    ]

    tipo_evento = models.CharField(max_length=30, choices=TIPO_EVENTO_CHOICES)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificaciones',
    )

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.tipo_evento} -> {self.usuario.correo}'
