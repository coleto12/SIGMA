from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Rol, Usuario, Estudiante, JefeDepartamento, Docente


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Usuario ya no usa 'username'; el login es por 'correo'. Se reutiliza
    UserAdmin (que sabe manejar el hashing de password) pero redefiniendo
    los fieldsets para los campos reales de este modelo.
    """
    model = Usuario
    ordering = ('correo',)
    list_display = ('id', 'correo', 'rol', 'is_active', 'is_staff')
    list_filter = ('rol', 'is_active', 'is_staff')
    search_fields = ('correo',)

    fieldsets = (
        (None, {'fields': ('correo', 'password')}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'rol', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre_completo', 'programa_academico', 'semestre_actual', 'usuario')
    list_filter = ('programa_academico', 'semestre_actual')
    search_fields = ('codigo', 'primer_nombre', 'primer_apellido')


@admin.register(JefeDepartamento)
class JefeDepartamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre_completo', 'programa_academico', 'usuario')
    search_fields = ('codigo', 'primer_nombre', 'primer_apellido')


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'primer_nombre', 'primer_apellido', 'correo', 'programa_academico')
    list_filter = ('programa_academico',)
    search_fields = ('codigo', 'primer_nombre', 'primer_apellido', 'correo')