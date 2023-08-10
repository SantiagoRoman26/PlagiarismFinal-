from django.urls import path
from . import views

urlpatterns = [
    # path('', views.autenticar, name="autenticar"),
    # path('solicitar/<int:usuario_id>', views.solicitarRol, name="solicitar_rol"),
    path('activar/<int:usuario_id>', views.generarRol, name="activar"),
    # path('registro', views.registrar, name="registrar"),
    # path('cambioClave', views.passwordChange, name="passwordChange"),
] 