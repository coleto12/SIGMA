from django.urls import path
from . import views

urlpatterns = [
    path('registros/', views.RegistroAuditoriaListView.as_view(), name='registro-auditoria-list'),
]