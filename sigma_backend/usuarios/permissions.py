"""
Permisos personalizados (RBAC) reutilizables en todas las apps de SIGMA.

Ver ERS - RNF-SEG-03 (Autorización basada en Roles): un usuario con rol
"Estudiante" que intente acceder a un endpoint o ruta administrativa debe
recibir HTTP 403 Forbidden. DRF ya devuelve 403 automáticamente cuando
has_permission() retorna False, así que estas clases solo necesitan
implementar esa comprobación.

Uso en una view:
    class AlgoQueSoloVeJefeView(APIView):
        permission_classes = [IsAuthenticated, EsJefeDepartamento]
"""
from rest_framework.permissions import BasePermission


def _rol_usuario(request):
    """Devuelve el nombre del rol del usuario autenticado, o None."""
    usuario = request.user
    if not usuario or not usuario.is_authenticated:
        return None
    return usuario.rol.nombre if usuario.rol else None


class EsEstudiante(BasePermission):
    message = 'Esta acción solo está disponible para usuarios con rol Estudiante.'

    def has_permission(self, request, view):
        return _rol_usuario(request) == 'Estudiante'


class EsJefeDepartamento(BasePermission):
    message = 'Esta acción solo está disponible para usuarios con rol Jefe de Departamento.'

    def has_permission(self, request, view):
        return _rol_usuario(request) == 'Jefe de Departamento'


class EsAdministrador(BasePermission):
    message = 'Esta acción solo está disponible para usuarios con rol Administrador.'

    def has_permission(self, request, view):
        return _rol_usuario(request) == 'Administrador'


class EsJefeDepartamentoOAdministrador(BasePermission):
    message = 'Esta acción requiere rol Jefe de Departamento o Administrador.'

    def has_permission(self, request, view):
        return _rol_usuario(request) in ('Jefe de Departamento', 'Administrador')