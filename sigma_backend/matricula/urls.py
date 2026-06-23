from django.urls import path
from . import views

urlpatterns = [
    path('periodos-matricula/', views.PeriodoMatriculaListCreateView.as_view(), name='periodo-matricula-list-create'),
    path('periodos-matricula/<int:pk>/', views.PeriodoMatriculaDetailView.as_view(), name='periodo-matricula-detail'),
    path('periodos-matricula/<int:pk>/reabrir/', views.PeriodoMatriculaReabrirView.as_view(), name='periodo-matricula-reabrir'),

    path('requisitos-documentales/', views.RequisitoDocumentalListCreateView.as_view(), name='requisito-documental-list-create'),
    path('requisitos-documentales/<int:pk>/', views.RequisitoDocumentalDetailView.as_view(), name='requisito-documental-detail'),

    path('solicitudes-matricula/', views.SolicitudMatriculaListCreateView.as_view(), name='solicitud-matricula-list-create'),
    path('solicitudes-matricula/<int:pk>/', views.SolicitudMatriculaDetailView.as_view(), name='solicitud-matricula-detail'),
    path('solicitudes-matricula/<int:pk>/aprobar/', views.SolicitudMatriculaAprobarView.as_view(), name='solicitud-matricula-aprobar'),
    path('solicitudes-matricula/<int:pk>/rechazar/', views.SolicitudMatriculaRechazarView.as_view(), name='solicitud-matricula-rechazar'),
    path('solicitudes-matricula/<int:pk>/confirmar-envio/', views.SolicitudMatriculaConfirmarEnvioView.as_view(), name='solicitud-matricula-confirmar-envio'),

    path('solicitudes-asignatura/', views.SolicitudAsignaturaListCreateView.as_view(), name='solicitud-asignatura-list-create'),
    path('solicitudes-asignatura/<int:pk>/', views.SolicitudAsignaturaDetailView.as_view(), name='solicitud-asignatura-detail'),

    path('documentos-adjuntos/', views.DocumentoAdjuntoListCreateView.as_view(), name='documento-adjunto-list-create'),
    path('documentos-adjuntos/<int:pk>/', views.DocumentoAdjuntoDetailView.as_view(), name='documento-adjunto-detail'),

    path('matriculas-oficiales/', views.MatriculaOficialListView.as_view(), name='matricula-oficial-list'),
    path('matriculas-oficiales/<int:pk>/', views.MatriculaOficialDetailView.as_view(), name='matricula-oficial-detail'),
]