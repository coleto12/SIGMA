"""
Rutas principales del proyecto SIGMA.
Cada app expondrá sus propias rutas bajo un prefijo /api/<bloque>/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def _diagnostico_correo_temporal(request):
    """
    TEMPORAL: endpoint de diagnóstico para aislar por qué los correos
    no llegan en producción (Railway). Intenta enviar un correo real y
    devuelve en la respuesta HTTP exactamente qué pasó, sin depender de
    que los logs del contenedor muestren algo. BORRAR después de
    diagnosticar.
    """
    import traceback
    from django.core.mail import send_mail
    destino = request.GET.get('correo', settings.EMAIL_HOST_USER)
    resultado = {
        'EMAIL_BACKEND': settings.EMAIL_BACKEND,
        'EMAIL_HOST': settings.EMAIL_HOST,
        'EMAIL_PORT': settings.EMAIL_PORT,
        'EMAIL_HOST_USER_configurado': bool(settings.EMAIL_HOST_USER),
        'EMAIL_HOST_PASSWORD_configurado': bool(settings.EMAIL_HOST_PASSWORD),
        'destino_prueba': destino,
    }
    try:
        enviados = send_mail(
            subject='SIGMA: correo de diagnóstico',
            message='Si recibes esto, el envío SMTP funciona correctamente desde Railway.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destino],
            fail_silently=False,
        )
        resultado['exito'] = True
        resultado['mensajes_enviados'] = enviados
    except Exception as error:
        resultado['exito'] = False
        resultado['error_tipo'] = type(error).__name__
        resultado['error_mensaje'] = str(error)
        resultado['traceback'] = traceback.format_exc()
    return JsonResponse(resultado)


urlpatterns = [
    path('admin/', admin.site.urls),

    # Rutas de cada bloque funcional (se irán agregando conforme
    # se construyan los serializers/views de cada app)
    path('api/institucional/', include('institucional.urls')),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/academico/', include('academico.urls')),
    path('api/programacion/', include('programacion.urls')),
    path('api/matricula/', include('matricula.urls')),
    path('api/notificaciones/', include('notificaciones.urls')),
    path('api/auditoria/', include('auditoria.urls')),

    # TEMPORAL - borrar después de diagnosticar el problema de correos:
    path('diagnostico-correo/', _diagnostico_correo_temporal, name='diagnostico-correo-temporal'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)