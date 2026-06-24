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
    vía Resend no llegan en producción. BORRAR después de diagnosticar.
    """
    import requests as requests_lib
    destino = request.GET.get('correo', 'soteroq@unicartagena.edu.co')
    resultado = {
        'RESEND_API_KEY_configurada': bool(settings.RESEND_API_KEY),
        'RESEND_API_KEY_primeros_caracteres': settings.RESEND_API_KEY[:6] if settings.RESEND_API_KEY else None,
        'RESEND_FROM_EMAIL': settings.RESEND_FROM_EMAIL,
        'destino_prueba': destino,
    }
    try:
        respuesta = requests_lib.post(
            'https://api.resend.com/emails',
            json={
                'from': settings.RESEND_FROM_EMAIL,
                'to': [destino],
                'subject': 'SIGMA: correo de diagnóstico',
                'text': 'Si recibes esto, Resend funciona correctamente desde Railway.',
            },
            headers={'Authorization': f'Bearer {settings.RESEND_API_KEY}'},
            timeout=10,
        )
        resultado['status_code'] = respuesta.status_code
        resultado['respuesta_body'] = respuesta.text
    except Exception as error:
        resultado['exito'] = False
        resultado['error_tipo'] = type(error).__name__
        resultado['error_mensaje'] = str(error)
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