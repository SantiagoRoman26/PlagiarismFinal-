from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name='documento'),
    path('upload', views.subir_archivo, name='subir_archivo'),
    path('visualizar/<int:gestion_id>/', views.visualizar_archivo, name='visualizar_archivo'),
    path('', views.index, name='documentos'),
    path('eliminarDocumento/<int:documento_id>/', views.eliminarDocumento, name='eliminar_documento'),
]

