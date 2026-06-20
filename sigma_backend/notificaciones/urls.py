from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificacionListView.as_view(), name='notificacion-list'),
    path('<int:pk>/', views.NotificacionDetailView.as_view(), name='notificacion-detail'),
    path('marcar-todas-leidas/', views.NotificacionMarcarTodasLeidasView.as_view(), name='notificacion-marcar-todas-leidas'),
]