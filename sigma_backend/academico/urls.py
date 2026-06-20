from django.urls import path
from . import views

urlpatterns = [
    path('periodos-academicos/', views.PeriodoAcademicoListCreateView.as_view(), name='periodo-academico-list-create'),
    path('periodos-academicos/<int:pk>/', views.PeriodoAcademicoDetailView.as_view(), name='periodo-academico-detail'),

    path('planes-estudio/', views.PlanEstudioListCreateView.as_view(), name='plan-estudio-list-create'),
    path('planes-estudio/<int:pk>/', views.PlanEstudioDetailView.as_view(), name='plan-estudio-detail'),

    path('asignaturas/', views.AsignaturaListCreateView.as_view(), name='asignatura-list-create'),
    path('asignaturas/<int:pk>/', views.AsignaturaDetailView.as_view(), name='asignatura-detail'),

    path('plan-asignaturas/', views.PlanEstudioAsignaturaListCreateView.as_view(), name='plan-asignatura-list-create'),
    path('plan-asignaturas/<int:pk>/', views.PlanEstudioAsignaturaDetailView.as_view(), name='plan-asignatura-detail'),

    path('prerrequisitos/', views.PrerrequisitoListCreateView.as_view(), name='prerrequisito-list-create'),
    path('prerrequisitos/<int:pk>/', views.PrerrequisitoDetailView.as_view(), name='prerrequisito-detail'),

    path('historial-academico/', views.HistorialAcademicoListCreateView.as_view(), name='historial-academico-list-create'),
    path('historial-academico/<int:pk>/', views.HistorialAcademicoDetailView.as_view(), name='historial-academico-detail'),
]