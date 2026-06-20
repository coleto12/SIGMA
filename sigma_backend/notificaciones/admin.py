from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo_evento', 'leida', 'created_at')
    list_filter = ('tipo_evento', 'leida')
    search_fields = ('usuario__correo', 'mensaje')
