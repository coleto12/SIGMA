"""
Rutas principales del proyecto SIGMA.
Cada app expondrá sus propias rutas bajo un prefijo /api/<bloque>/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)