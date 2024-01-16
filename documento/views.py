import os
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from modelo.models import Documento, Usuario, GestionDocumentos, Estudiante, Docente, Resultado
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

@login_required
def subir_archivo(request):
    user = request.user
    usuario = Usuario.objects.get(correo=user.email)
    print(usuario.usuario_id)
    if usuario.estado:
        if request.method == 'POST':
            
            # documento=Documento.objects.filter(usuario=usuario).last()
            # documento.visible = False
            # documento.save()
            documento = Documento()
            archivo = request.FILES['archivo']
            ext = os.path.splitext(archivo.name)[-1].lower()
            if ext == '.pdf':
                documento.tipo = 'pdf'
            elif ext in ['.doc', '.docx']:
                documento.tipo = 'word'
            elif ext == '.txt':
                documento.tipo = 'texto'
            else:
                documento.tipo = 'other'
            # documento.usuario = usuario
            documento.archivo = archivo
            documento.visible = True
            gestion = GestionDocumentos()

            if user.groups.filter(name = "docente").exists() or user.groups.filter(name = "admin").exists():
                docente = Docente.objects.get(usuario = usuario)
                ########################################
                if GestionDocumentos.objects.filter(docente = docente).exists():
                    listaGestion = GestionDocumentos.objects.filter(docente = docente).last()
                    
                    ultimo_documento = listaGestion.documento
                    ultimo_documento.visible = False
                    ultimo_documento.save()
                #######################################
                documento.save()
                
                
                gestion.docente = docente
                gestion.documento = documento
                gestion.save()

            elif user.groups.filter(name = "estudiante").exists():
                estudiante = Estudiante.objects.get(usuario = usuario)
                if GestionDocumentos.objects.filter(estudiante = estudiante).exists():
                    listaGestion = GestionDocumentos.objects.filter(estudiante = estudiante).last()
                    if listaGestion.docente is not None:
                        ultimo_documento = listaGestion.documento
                        ultimo_documento.visible = False
                        ultimo_documento.save()
                    else:
                        print("aqui ",listaGestion.gestion_id)
                        try:
                            resultado = Resultado.objects.get(management = listaGestion)
                            resultado.delete()
                        except Resultado.DoesNotExist:
                            print("no se encontro un resultado")
                        last_documento = listaGestion.documento
                        last_documento.delete()
                        
                        listaGestion.delete()
                
                documento.save()
                gestion.estudiante = estudiante
                gestion.documento = documento
                gestion.save()

                # response_data = {'redirect_url': reverse('gestion_estudiante', args=[documento.documento_id])} #Cambio quitarlo para pasarlo a un resultado, ademas ligarlo a gestion en vez de a solo documento
                # return JsonResponse(response_data)
                # return HttpResponseRedirect(reverse('gestion_estudiante', args=[estudiante.estudiante_id, documento.documento_id]))
            else:
                return HttpResponseRedirect(reverse('no_activo'))

            # return redirect(visualizar_archivo,documento.documento_id)
            directorio_archivo = os.path.dirname(documento.archivo.path)
            print("----------------------------------------")
            ruta_completa = documento.archivo.path
            print ("directorio_archivo completo=",ruta_completa)
            directorio, nombre_archivo = os.path.split(ruta_completa)
            print("Directorio:", directorio)
            print("Nombre del archivo:", nombre_archivo)
            print("----------------------------------------")
            response_data = {'redirect_url': reverse('visualizar_archivo', args=[gestion.gestion_id])}
            return JsonResponse(response_data)
            # else:
            #     return render(request,'documento/subir_archivo.html',{'mensaje':'Usuario no encontrado'}) #ojo registrar el usuario, en el caso de un registro erroneo
        return  render(request, 'documento/subir_archivo.html')
    else :
        return render(request, 'homepage.html')
#Cambio por realizar en la logica, antes de almacenar el archivo, deberia ser posible subir el archivo solo para ver una visualizacion del documento a analizar
#una vez seleccionado para analizar el documento debe guardarse, se puede mandar a anlizar o cancelar el documento que se subio.
#hacerlo con cronjob, si es posible
@login_required
def visualizar_archivo(request, gestion_id):
    user = request.user
    usuario = Usuario.objects.get(correo=user.email)
    gestion = GestionDocumentos.objects.get(gestion_id = gestion_id)
    documento = gestion.documento #ojo
    if usuario.estado and documento.estado:
        if request.method == 'GET': #Cambio post bajar toda la logica fuera del return. 7-   
            context = {
            'gestion' : gestion,
            'documento': documento,
            }
            return render(request, 'documento/visualizar.html', context)
        
        return render(request,'documento/visualizar.html', context)
    else:
        return render(request, 'homepage.html')
    
    # documento = Documento.objects.get(documento_id = gestion.documento_id)
    
@login_required
def index(request):
    
    user = request.user
    usuario = Usuario.objects.get(correo=user.email)
    listaDocumentos = []
    if usuario.estado:
        message = request.GET.get('message')
        if (user.groups.filter(name = "docente").exists()):
            docente = Docente.objects.get(usuario = usuario)
            listaGestion = GestionDocumentos.objects.filter(docente = docente)
            
            for gestion in listaGestion:
                cond = False
                try:
                    resultado = Resultado.objects.get(management= gestion)
                    #listaDocumentos.append(resultado)
                    cond = "Analizado"
                except Resultado.DoesNotExist:
                     cond = "Por analizar"
                documento_dict = {**gestion.documento.__dict__, 'analizado': cond, 'nombre': gestion.documento.get_nombre_archivo}
                listaDocumentos.append(documento_dict)
            return render (request, 'documento/index.html', locals())
        elif (user.groups.filter(name = "estudiante").exists()):
            estudiante = Estudiante.objects.get(usuario = usuario)
            listaGestion = GestionDocumentos.objects.filter(estudiante = estudiante)
            for gestion in listaGestion:
                listaDocumentos.append(gestion.documento)
            return render (request, 'documento/index.html', locals())
    return render(request, 'homepage.html')

@login_required
def eliminarDocumento(request, documento_id):
    user = request.user
    if user.groups.filter(name = "docente").exists() :
        try:
            documento = Documento.objects.get(documento_id = documento_id)
            gestion = GestionDocumentos.objects.filter(documento=documento)
            documento.delete()
            gestion.delete()
            return redirect(index)
        except Exception  as e:
            print("error")
            return redirect(index)
            
    else:
        return render(request, 'login/forbidden.html', locals())
    