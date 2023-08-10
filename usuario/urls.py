from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='usuarios'),
    path('autorizaciones', views.autorizaciones, name='autorizaciones'),
    path('eliminarUsuario/<int:usuario_id>/', views.eliminarUsuario, name='eliminar_usuario'),
    path('modificarUsuario/<int:usuario_id>/', views.modificarUsuario, name='modificar_usuario'),
    path('rolUsuario/<int:usuario_id>/', views.cambiarRolUsuario, name="rol_usuario"),
    path('generarUsuario', views.generarUsuario, name="generar_usuario")
    
]