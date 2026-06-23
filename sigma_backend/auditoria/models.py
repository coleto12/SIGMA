"""
Registro de auditoría transversal (ver CU09 - Modificar Programación
Académica: "Cualquier modificación realizada debe quedar registrada en
los logs del sistema junto con la fecha, hora y usuario que realizó el
cambio").

No está atado a un modelo específico (Grupo, HorarioGrupo, etc.) para
poder reutilizarse en cualquier entidad que en el futuro necesite el
mismo tipo de trazabilidad, sin tener que crear una tabla de logs por
cada modelo.
"""
from django.db import models
from django.conf import settings


class RegistroAuditoria(models.Model):
    ACCION_CHOICES = [
        ('crear', 'Crear'),
        ('modificar', 'Modificar'),
        ('eliminar', 'Eliminar'),
    ]

    fecha_hora = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registros_auditoria',
        help_text='Usuario que realizó la acción. Se conserva null si el usuario fue eliminado después.',
    )
    accion = models.CharField(max_length=10, choices=ACCION_CHOICES)
    modelo_afectado = models.CharField(max_length=100, help_text="Ej. 'Grupo', 'HorarioGrupo'.")
    objeto_id = models.PositiveIntegerField(help_text='Id del registro afectado dentro de su propia tabla.')
    descripcion = models.TextField(
        help_text='Resumen legible del cambio, ej. "Cambió docente de Laura Martínez a Carlos Gómez".'
    )

    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-fecha_hora']

    def __str__(self):
        correo = self.usuario.correo if self.usuario else 'usuario eliminado'
        return f'{self.fecha_hora:%Y-%m-%d %H:%M} - {correo} - {self.accion} {self.modelo_afectado}#{self.objeto_id}'