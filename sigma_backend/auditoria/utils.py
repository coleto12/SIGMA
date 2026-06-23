"""
Función helper para registrar auditoría desde cualquier vista, sin
tener que repetir la lógica de creación del RegistroAuditoria en cada
lugar donde se modifica un Grupo, HorarioGrupo, etc.

Uso típico (ver programacion/views.py, GrupoDetailView.put):
    from auditoria.utils import registrar_auditoria
    registrar_auditoria(
        request, accion='modificar', modelo_afectado='Grupo', objeto_id=grupo.id,
        descripcion=f'Cambió docente de "{docente_anterior}" a "{docente_nuevo}".',
    )
"""
from .models import RegistroAuditoria


def registrar_auditoria(request, *, accion, modelo_afectado, objeto_id, descripcion):
    usuario = request.user if request.user.is_authenticated else None
    RegistroAuditoria.objects.create(
        usuario=usuario,
        accion=accion,
        modelo_afectado=modelo_afectado,
        objeto_id=objeto_id,
        descripcion=descripcion,
    )