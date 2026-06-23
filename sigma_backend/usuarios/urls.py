from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import carga_csv

urlpatterns = [
    # Autenticación
    path('login/', views.LoginView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login-refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.MeView.as_view(), name='me'),

    # Recuperación de contraseña
    path('recuperar-contrasena/', views.SolicitarRecuperacionContrasenaView.as_view(), name='recuperar-contrasena'),
    path('restablecer-contrasena/', views.ConfirmarRecuperacionContrasenaView.as_view(), name='restablecer-contrasena'),

    # Estudiante
    path('estudiantes/', views.EstudianteListCreateView.as_view(), name='estudiante-list-create'),
    path('estudiantes/<int:pk>/', views.EstudianteDetailView.as_view(), name='estudiante-detail'),

    # JefeDepartamento
    path('jefes-departamento/', views.JefeDepartamentoListCreateView.as_view(), name='jefe-departamento-list-create'),
    path('jefes-departamento/<int:pk>/', views.JefeDepartamentoDetailView.as_view(), name='jefe-departamento-detail'),

    # Docente
    path('docentes/', views.DocenteListCreateView.as_view(), name='docente-list-create'),
    path('docentes/<int:pk>/', views.DocenteDetailView.as_view(), name='docente-detail'),

    # Carga de Información Académica vía CSV (CU02)
    path('cargar/docentes/', carga_csv.CargarDocentesView.as_view(), name='cargar-docentes'),
]