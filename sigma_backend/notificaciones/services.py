"""
Funciones utilitarias para crear Notificaciones desde otros bloques del
sistema (matricula, programacion, etc.) sin duplicar lógica de creación.

Cada llamada a notificar() hace dos cosas:
1) Crea el registro in-app en la tabla Notificacion (como antes).
2) Envía un correo real al usuario usando la configuración SMTP de
   settings.py (Gmail). Si las credenciales no están configuradas,
   Django usa el backend de consola (ver settings.py) y el "correo"
   simplemente se imprime en la terminal del servidor, sin fallar.

Uso típico desde matricula/views.py:
    from notificaciones.services import notificar

    notificar(
        usuario=solicitud.estudiante.usuario,
        tipo_evento='solicitud_aprobada',
        mensaje=f'Tu solicitud de matrícula #{solicitud.pk} fue aprobada.',
    )
"""
from django.core.mail import send_mail
from django.conf import settings
from .models import Notificacion

# Asuntos legibles para cada tipo de evento (se usan en el correo).
_ASUNTOS_POR_TIPO_EVENTO = {
    'solicitud_recibida': 'SIGMA: solicitud de matrícula recibida',
    'solicitud_aprobada': 'SIGMA: tu solicitud de matrícula fue aprobada',
    'solicitud_rechazada': 'SIGMA: tu solicitud de matrícula fue rechazada',
    'matricula_generada': 'SIGMA: tu matrícula oficial está disponible',
    'fecha_limite_proxima': 'SIGMA: fecha límite próxima',
}


def notificar(usuario, tipo_evento, mensaje):
    """
    Crea una Notificacion para 'usuario' y le envía un correo con el mismo
    contenido. Ningún fallo aquí (en la notificación in-app o en el envío
    de correo) debe propagar una excepción hacia quien llama: un problema
    al notificar nunca debe tumbar el flujo de negocio principal (p.ej.
    la aprobación de una SolicitudMatricula).
    """
    if usuario is None:
        return None

    notificacion = None
    try:
        notificacion = Notificacion.objects.create(
            usuario=usuario,
            tipo_evento=tipo_evento,
            mensaje=mensaje,
        )
    except Exception:
        # En un sistema productivo esto se registraría en logs (logging.exception).
        pass

    _enviar_correo(usuario, tipo_evento, mensaje)

    return notificacion


def _enviar_correo(usuario, tipo_evento, mensaje):
    correo_destino = getattr(usuario, 'correo', None)
    if not correo_destino:
        return
    try:
        asunto = _ASUNTOS_POR_TIPO_EVENTO.get(tipo_evento, 'SIGMA: nueva notificación')
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[correo_destino],
            fail_silently=True,
        )
    except Exception:
        # Igual que con la notificación in-app: un fallo de correo (SMTP
        # caído, credenciales inválidas, etc.) no debe romper el flujo
        # de negocio que disparó la notificación.
        pass