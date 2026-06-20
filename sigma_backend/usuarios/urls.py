from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.LoginView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login-refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.MeView.as_view(), name='me'),

    # Estudiante
    path('estudiantes/', views.EstudianteListCreateView.as_view(), name='estudiante-list-create'),
    path('estudiantes/<int:pk>/', views.EstudianteDetailView.as_view(), name='estudiante-detail'),

    # JefeDepartamento
    path('jefes-departamento/', views.JefeDepartamentoListCreateView.as_view(), name='jefe-departamento-list-create'),
    path('jefes-departamento/<int:pk>/', views.JefeDepartamentoDetailView.as_view(), name='jefe-departamento-detail'),

    # Docente
    path('docentes/', views.DocenteListCreateView.as_view(), name='docente-list-create'),
    path('docentes/<int:pk>/', views.DocenteDetailView.as_view(), name='docente-detail'),
]