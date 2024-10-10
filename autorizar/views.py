from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from modelo.models import Usuario, Docente, Estudiante
from django.contrib import messages
from .forms import FormularioAutorizacion
from correo.views import emailRegistroCompletado

# #app autorizar 
# def solicitarRol (request, usuario_id):
#     user = request.user 
#     usuario = Usuario.objects.get(usuario_id=usuario_id)
#     if request.method == 'POST':
#         role = request.POST.get('role')            
#         if role == 'teacher':
#             usuario.autorizado = True
#             usuario.estado = False
#             usuario.save()
#         else:
#             return render(request, 'login/deactive.html')                                             #pagina de muestra de errores
#         return HttpResponseRedirect(reverse('autenticar'))
#     return render(request, 'autorizar/solicitarRol.html') 


@login_required
def generarRol (request,usuario_id):
    user = request.user
    if user.is_superuser:
        usuario = Usuario.objects.get(usuario_id=usuario_id)
        formulario_autorizacion = FormularioAutorizacion(request.POST)

        if request.method == 'POST':
            if formulario_autorizacion.is_valid():
                opcion_seleccionada = formulario_autorizacion.cleaned_data['seleccion']
                if opcion_seleccionada == 'autorizar':
                    user = User.objects.get(email = usuario.correo)
                    if usuario.autorizado:
                        
                        docente_model = Docente()
                        docente_model.usuario = usuario
                        usuario.autorizado = True                           # el usuario es considerado un docente
                        usuario.estado = True 
                        docente_grupo=Group.objects.get(name='docente')
                        user.groups.add(docente_grupo)
                        user.save()
                        usuario.save()
                        
                        docente_model.save()
                        print('docente Guardado')
                    else:
                        estudiante_model = Estudiante()                     # el usuario es considerado un estudiante
                        estudiante_model.usuario = usuario
                        usuario.estado = True 
                        usuario.save()
                        estudiante_grupo=Group.objects.get(name='estudiante')
                        user.groups.add(estudiante_grupo)
                        user.save()
                        estudiante_model.save()
                        print('estudainte Guardado')
                    nombre = usuario.nombres +" " + usuario.apellidos
                    url = request.build_absolute_uri(reverse('autenticar'))
                    messages.success(request, 'Usuario autorizado')
                    emailRegistroCompletado(usuario.correo,nombre, url)
                else:
                    usuario.delete()
                    print('usuario descartado')
                return HttpResponseRedirect(reverse('homepage'))
        return render(request, 'autorizar/autorizar.html',locals()) 
    return render(request, 'login/forbidden.html') 