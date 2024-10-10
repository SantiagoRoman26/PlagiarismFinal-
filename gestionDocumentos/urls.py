from django.urls import path
from . import views

urlpatterns = [
    # path('', views.autenticar, name="autenticar"),
    path('estudiante/<int:gestion_id>', views.gestionEstudiante, name="gestion_estudiante"),
] 