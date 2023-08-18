"""
URL configuration for PlagiarismDetector project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
    MEDIA_URL
    MEDIA_ROOT
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('documento/', include('documento.urls')),
    path('usuario/', include('usuario.urls')),
    path('plagio/',include('plagio.urls')),
    path('autorizar/',include('autorizar.urls')),
    path('asignacion/',include('gestionDocumentos.urls')),
    
    path('prueba/', views.prueba, name='prueba'),
    path('login/', include('login.urls')),
    path('about/', views.about, name='about'),
    path('', views.index, name='homepage'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

