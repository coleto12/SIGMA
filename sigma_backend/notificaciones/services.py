"""
Funciones utilitarias para crear Notificaciones desde otros bloques del
sistema (matricula, programacion, etc.) sin duplicar lógica de creación.

Cada llamada a notificar() hace dos cosas:
1) Crea el registro in-app en la tabla Notificacion (como antes).
2) Envía un correo real al usuario vía la API HTTP de Resend
   (https://resend.com). Se usa la API en vez de SMTP directo porque
   Railway bloquea las conexiones salientes al puerto SMTP (587) por
   política de red ("OSError: Network is unreachable" - diagnosticado
   en producción). La API de Resend viaja por HTTPS (puerto 443).
   Si RESEND_API_KEY no está configurada, el envío simplemente se
   omite (se loguea, no se intenta), sin fallar.

Uso típico desde matricula/views.py:
    from notificaciones.services import notificar

    notificar(
        usuario=solicitud.estudiante.usuario,
        tipo_evento='solicitud_aprobada',
        mensaje=f'Tu solicitud de matrícula #{solicitud.pk} fue aprobada.',
    )
"""
import requests
from django.conf import settings
from .models import Notificacion

# Asuntos legibles para cada tipo de evento (se usan en el correo).
_ASUNTOS_POR_TIPO_EVENTO = {
    'solicitud_recibida': 'SIGMA: solicitud de matrícula recibida',
    'solicitud_aprobada': 'SIGMA: tu solicitud de matrícula fue aprobada',
    'solicitud_rechazada': 'SIGMA: tu solicitud de matrícula fue rechazada',
    'matricula_generada': 'SIGMA: tu matrícula oficial está disponible',
    'fecha_limite_proxima': 'SIGMA: fecha límite próxima',
    'recuperacion_contrasena': 'SIGMA: restablece tu contraseña',
}

_RESEND_API_URL = 'https://api.resend.com/emails'


def notificar(usuario, tipo_evento, mensaje, archivo_adjunto=None, nombre_adjunto=None):
    """
    Crea una Notificacion para 'usuario' y le envía un correo con el mismo
    contenido. Ningún fallo aquí (en la notificación in-app o en el envío
    de correo) debe propagar una excepción hacia quien llama: un problema
    al notificar nunca debe tumbar el flujo de negocio principal (p.ej.
    la aprobación de una SolicitudMatricula).

    archivo_adjunto: objeto tipo Django File/ContentFile (opcional). Si se
    pasa, se adjunta al correo en base64 (formato que espera la API de
    Resend), por ejemplo el PDF de la matrícula oficial.
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

    _enviar_correo(usuario, tipo_evento, mensaje, archivo_adjunto, nombre_adjunto)

    return notificacion


def _enviar_correo(usuario, tipo_evento, mensaje, archivo_adjunto=None, nombre_adjunto=None):
    correo_destino = getattr(usuario, 'correo', None)
    if not correo_destino:
        return

    if not settings.RESEND_API_KEY:
        print(
            f'[notificaciones] RESEND_API_KEY no configurada; '
            f'se omite el envío de correo a {correo_destino}.',
            flush=True,
        )
        return

    asunto = _ASUNTOS_POR_TIPO_EVENTO.get(tipo_evento, 'SIGMA: nueva notificación')
    # Resend espera el cuerpo de texto plano en 'text' (también soporta
    # 'html', no usado aquí). Los saltos de línea de mensaje se
    # respetan tal cual.
    payload = {
        'from': settings.RESEND_FROM_EMAIL,
        'to': [correo_destino],
        'subject': asunto,
        'text': mensaje,
    }

    if archivo_adjunto is not None:
        import base64
        # archivo_adjunto suele ser un FieldFile (ej. MatriculaOficial.documento).
        # Con storage remoto (Cloudinary) hay que abrirlo explícitamente antes
        # de leer; .seek()/.read() solos pueden fallar o devolver vacío si el
        # archivo no está abierto.
        archivo_adjunto.open('rb')
        contenido_binario = archivo_adjunto.read()
        archivo_adjunto.close()
        payload['attachments'] = [{
            'filename': nombre_adjunto or 'documento.pdf',
            'content': base64.b64encode(contenido_binario).decode('ascii'),
        }]

    try:
        respuesta = requests.post(
            _RESEND_API_URL,
            json=payload,
            headers={'Authorization': f'Bearer {settings.RESEND_API_KEY}'},
            timeout=10,
        )
        respuesta.raise_for_status()
    except Exception as error:
        # Igual que con la notificación in-app: un fallo de correo (API
        # caída, credenciales inválidas, límite de envíos excedido,
        # etc.) no debe romper el flujo de negocio que disparó la
        # notificación.
        # TODO: cambiar este print por logging.exception en producción.
        print(f'[notificaciones] No se pudo enviar el correo a {correo_destino}: {error}', flush=True)