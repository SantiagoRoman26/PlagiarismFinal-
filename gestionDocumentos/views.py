from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from modelo.models import Documento, Usuario, GestionDocumentos, Estudiante, Docente
from django.contrib.auth.decorators import login_required
from .forms import FormularioGestion
from django.contrib import messages

# Create your views here.
@login_required
def gestionEstudiante (request,gestion_id):
    user = request.user
    usuario_global = Usuario.objects.get(correo=user.email)
    if usuario_global.estado:
        formulario_gestion = FormularioGestion(request.POST)
        if request.method == 'POST':
            print("Datos limpios del formulario de gestion:", formulario_gestion)
            if formulario_gestion.is_valid():
                datos_gestion = formulario_gestion.cleaned_data
                #verificar que el email del docente exista
                email_docente = datos_gestion.get('email')
                if Usuario.objects.filter(correo=email_docente).exists():
                    #verificar si el usuario esta registrado como docente
                    print(" ################################################################################## ")
                    print(" verificar si el correo esta asociado a un docente ")
                    print(" ################################################################################## ")
                    usuario = Usuario.objects.get(correo=email_docente)
                    if Docente.objects.filter(usuario = usuario).exists() or user.groups.filter(name = "docente").exists():
                        print("aqui")
                        listaGestion = GestionDocumentos.objects.get (gestion_id = gestion_id)
                        documento = listaGestion.documento

                        listaGestion.titulo = datos_gestion.get('titulo')
                        listaGestion.comentario = datos_gestion.get('comentario')
                        listaGestion.docente = Docente.objects.get(usuario = usuario)
                        listaGestion.save()
                        documento.visible = True
                        documento.save()
                        #'detectar' gestion.gestion_id
                        #return render(request, 'gestion/exito.html',locals())
                        return HttpResponseRedirect(reverse('detectar', args=[listaGestion.gestion_id]))
                    else:
                        return HttpResponseRedirect(reverse('homepage'))
                else:
                    return HttpResponseRedirect(reverse('homepage'))
            else:
                messages.error(request, 'Corrige los errores.')
            print("no valido")    
            return render(request, 'gestion/gestionEstudiante.html',locals())
        
        return render(request, 'gestion/gestionEstudiante.html',locals())
    else:
        return render(request, 'homepage.html')