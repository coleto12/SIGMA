from django.urls import path
from . import views

urlpatterns = [
    path('programaciones-academicas/', views.ProgramacionAcademicaListCreateView.as_view(), name='programacion-academica-list-create'),
    path('programaciones-academicas/<int:pk>/', views.ProgramacionAcademicaDetailView.as_view(), name='programacion-academica-detail'),
    path('programaciones-academicas/<int:pk>/publicar/', views.ProgramacionAcademicaPublicarView.as_view(), name='programacion-academica-publicar'),

    path('salones/', views.SalonListCreateView.as_view(), name='salon-list-create'),
    path('salones/<int:pk>/', views.SalonDetailView.as_view(), name='salon-detail'),

    path('grupos/', views.GrupoListCreateView.as_view(), name='grupo-list-create'),
    path('grupos/<int:pk>/', views.GrupoDetailView.as_view(), name='grupo-detail'),

    path('horarios/', views.HorarioGrupoListCreateView.as_view(), name='horario-grupo-list-create'),
    path('horarios/<int:pk>/', views.HorarioGrupoDetailView.as_view(), name='horario-grupo-detail'),
]