from django.urls import path
from . import views

urlpatterns = [
    path('campus/', views.CampusListCreateView.as_view(), name='campus-list-create'),
    path('campus/<int:pk>/', views.CampusDetailView.as_view(), name='campus-detail'),

    path('facultades/', views.FacultadListCreateView.as_view(), name='facultad-list-create'),
    path('facultades/<int:pk>/', views.FacultadDetailView.as_view(), name='facultad-detail'),

    path('niveles-formacion/', views.NivelFormacionListCreateView.as_view(), name='nivel-formacion-list-create'),
    path('niveles-formacion/<int:pk>/', views.NivelFormacionDetailView.as_view(), name='nivel-formacion-detail'),

    path('programas-academicos/', views.ProgramaAcademicoListCreateView.as_view(), name='programa-academico-list-create'),
    path('programas-academicos/<int:pk>/', views.ProgramaAcademicoDetailView.as_view(), name='programa-academico-detail'),
]