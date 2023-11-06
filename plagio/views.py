import json
from django.shortcuts import render, redirect
from modelo.models import Documento, Usuario, Resultado, GestionDocumentos, Docente, Estudiante
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from nlp.src.python import main
from correo.views import emailCompartir,emailResultado
import threading
from asgiref.sync import sync_to_async
 

# Esta logica solo funciona en la fase de pruebas, en produccion se debe tomar el documento desde la ruta base, en donde se va a cambiar el config para ingresar al
# documento a analizar.
@login_required
def detectar(request, gestion_id):
    user = request.user
    usuario = Usuario.objects.get(correo=user.email)
    gestion = GestionDocumentos.objects.get(gestion_id=gestion_id)
    documento = gestion.documento
    if usuario.estado and documento.estado:
        directorio_archivo = documento.archivo.path
        resultado = Resultado()
        resultado.management = gestion
        resultado.ejecutando = True
        resultado.save()
        
        documento.estado = False
        documento.save()
        # Ejecutar el proceso asíncrono en un hilo separado
        threading.Thread(target=processo_asincrono, args=(gestion_id, directorio_archivo, usuario.correo,user)).start()

        # Continuar con la lógica de la vista después de que termine el proceso asíncrono
        return render (request, 'documento/ejecutando.html', locals())
    return render(request, 'homepage.html')
# Tu función asíncrona processo_asincrono
def processo_asincrono(gestion_id, directorio_archivo, correo,user):
    lista_archivos = obtener_documentos(user)
    # Lógica para el proceso asíncrono, por ejemplo, llamar a main.main()
    gestion = GestionDocumentos.objects.get(gestion_id=gestion_id)
    documento_generado, nombre, plagio, informacion = main.main(directorio_archivo,lista_archivos)

    # Actualizar el resultado en la base de datos después de que termine el proceso
    
    resultado = Resultado.objects.get(management=gestion)
    resultado.ejecutando = False
    resultado.archivo.save(nombre, ContentFile(open(documento_generado, 'rb').read()), save=False)
    resultado.estado = True
    resultado.plagio = plagio
    resultado.informacion = informacion
    resultado.save()
    emailResultado(correo)
    return HttpResponseRedirect(reverse('revision', args=[resultado.resultado_id]))

def obtener_documentos(user):
    usuario = Usuario.objects.get(correo=user.email)
    listaDocumentos = []
    if (user.groups.filter(name = "docente").exists()):
        docente = Docente.objects.get(usuario = usuario)
        listaGestion = GestionDocumentos.objects.filter(docente = docente)
        for gestion in listaGestion:
            try:
                resultado = Resultado.objects.get(management= gestion)
                listaDocumentos.append(gestion.documento.get_nombre_archivo)
            except Resultado.DoesNotExist:
                    print("el resultado esta procesandose, o no existe en la base de datos")
            
    elif (user.groups.filter(name = "estudiante").exists()):
        estudiante = Estudiante.objects.get(usuario = usuario)
        listaGestion = GestionDocumentos.objects.filter(estudiante = estudiante)
        for gestion in listaGestion:
            try:
                resultado = Resultado.objects.get(management = gestion)
                listaDocumentos.append(gestion.documento.get_nombre_archivo)
            except Resultado.DoesNotExist:
                print("el resultado esta procesandose, o no existe en la base de datos")
            
    return listaDocumentos
    
@login_required
def index(request):
    user = request.user
    usuario = Usuario.objects.get(correo=user.email)
    if usuario.estado:
        if user.groups.filter(name = "docente").exists() or user.groups.filter(name = "admin").exists():
            cond = False
            docente = Docente.objects.get(usuario = usuario)
            listaGestion = GestionDocumentos.objects.filter(docente = docente)
            listaResultado = []
            for gestion in listaGestion:
                try:
                    print(gestion.gestion_id)
                    resultado = Resultado.objects.get(management= gestion)
                    listaResultado.append(resultado)
                    if gestion.estudiante:
                        cond = True
                except Resultado.DoesNotExist:
                     print("el resultado esta procesandose, o no existe en la base de datos")
        elif user.groups.filter(name = "estudiante").exists():
            estudiante = Estudiante.objects.get(usuario = usuario)
            listaGestion = GestionDocumentos.objects.filter(estudiante = estudiante)
            listaResultado = []
            for gestion in listaGestion:
                try:
                    print(gestion.gestion_id)
                    if gestion.docente is not None:
                        resultado = Resultado.objects.get(management=gestion)
                        listaResultado.append(resultado)
                        cond = True
                    else:
                        print('No tiene asignado un profesor para realizar el plagio.')
                except Resultado.DoesNotExist:
                     print("el resultado esta procesandose, o no existe en la base de datos")
            pass
        # busqueda = request.POST.get("busqueda")
        return render (request, 'plagio/index.html', locals())
    return render(request, 'homepage.html')

@login_required
def revision(request,resultado_id):
    #cambio agregar logicca de documento publico 
    user = request.user
    usuario = Usuario.objects.get(correo=user.email)
    if usuario.estado:
        resultado = Resultado.objects.get(resultado_id = resultado_id)
        gestion = GestionDocumentos.objects.get(resultado = resultado)
        return render(request,'plagio/Success.html',locals())
    return

@login_required
def eliminarResultado(request, resultado_id):
    user = request.user
    if user.groups.filter(name = "docente").exists() or user.groups.filter(name = "admin").exists():
        try:
            resultado = Resultado.objects.get(resultado_id = resultado_id)
            gestion = resultado.management
            resultado.delete()
            gestion.delete()
            return redirect(index)
        except Exception  as e:
            print("error")
            return redirect(index)
            
    else:
        return render(request, 'login/forbidden.html', locals())

@login_required
def compartirDocumento(request, resultado_id):
    user = request.user
    usuario = Usuario.objects.get(correo=user.email)
    nombres = usuario.nombres +" "+ usuario.apellidos
    resultado = Resultado.objects.get(resultado_id = resultado_id)
    if request.method == 'POST':
        # Obtener los correos electrónicos ingresados en el formulario
        correos = request.POST.getlist('correo')

        # Obtener el comentario ingresado en el formulario
        comentario = request.POST.get('comentario', '')

        
        archivo_adjunto = resultado.archivo

        # Por ejemplo, enviar correos electrónicos a las direcciones ingresadas
        emailCompartir(correos, comentario, nombres, archivo_adjunto)
        return redirect(index)
    return render(request, 'plagio/compartir.html',locals())
    
@login_required
def detalleDocumento(request, resultado_id):
    user = request.user
    resultado = Resultado.objects.get(resultado_id = resultado_id)
    plagio = resultado.plagio
    if user.groups.filter(name = "docente").exists() or user.groups.filter(name = "admin").exists():
        listaOracion=[]
        listaPlagio=[]
        listaPorcentaje=[]
        listaUrl=[]
        listaUbicacion=[]
        for oracion, plagio, porcentaje, url, ubicacion in plagio:
            listaOracion.append(oracion)
            listaPlagio.append(plagio)
            listaPorcentaje.append(porcentaje)
            listaUrl.append(url)
            listaUbicacion.append(ubicacion)
        
        matriz = []
        print("plagio",len(listaOracion))
        for i in range(len(listaOracion)):
            fila = [listaOracion[i], listaPlagio[i], listaPorcentaje[i], listaUrl[i],listaUbicacion[i]]
            matriz.append(fila)
        num_oraciones = resultado.informacion['total_oraciones']
        context = {
            'matriz': matriz,
            'resultado': resultado,
            'num_oraciones' : num_oraciones,
        }
        
        return render(request, 'plagio/matrizDetalle.html', context)
    else:
        return render(request, 'login/forbidden.html', locals())

@login_required
def eliminar_filas(request, resultado_id):
    if request.method == 'POST':
        resultado = Resultado.objects.get(resultado_id=resultado_id)
        plagio = resultado.plagio

        # Obtener las filas eliminadas desde el formulario
        filas_eliminadas = request.POST.getlist('filas_eliminadas')
        filas_eliminadas = json.loads(filas_eliminadas[0])
        print("filas_eliminadas",filas_eliminadas)

        # Eliminar las filas seleccionadas de la matriz plagio
        plagio_actualizado = [fila for i, fila in enumerate(plagio) if i not in map(int, filas_eliminadas)]
        print("plagio actualizado cantidad",len(plagio_actualizado))
        # Actualizar el campo plagio del objeto resultado
        

        informacion = resultado.informacion
        # porcentaje_de_plagio = (len(plagio_actualizado) / resultado.informacion['total_oraciones']) * 100
        porcentaje_de_plagio = 0
        for oracion, plagio, porcentaje, url, ubicacion in plagio_actualizado:
            porcentaje_de_plagio += porcentaje
        porcentaje_de_plagio = (porcentaje_de_plagio / len(plagio)) *100
        
        print("porcentaje_de_plagio = ", porcentaje_de_plagio)
        informacion['porcentaje_de_plagio'] = porcentaje_de_plagio
        print("resultado.archivo.path = ",resultado.archivo.path)
        documento_generado, nombre= main.regenerarResultado(informacion['nombre_archivo'],informacion['topico_con_mas_score'],plagio_actualizado,informacion['tiempo_que_tardo'],informacion['porcentaje_de_plagio'],informacion['path_resultado'],informacion['path_referencia'],resultado.archivo.path)
        resultado.plagio = plagio_actualizado
        with open(documento_generado, 'rb') as archivo:
            archivo_django = ContentFile(archivo.read(), name=nombre)

        resultado.archivo.save(nombre, archivo_django)
        resultado.save()

        # Devolver una respuesta JSON exitosa
        return redirect('detalle_documento', resultado_id)

    # Redireccionar de vuelta a la página de la tabla en caso de que no sea una solicitud POST
    return redirect('detalle_documento', resultado_id)

#por realizar: Se debe enviar denuevo el resultado.plagio al script de python para actualizar el documento, adicionalmente obtener las oraciones en total del resultado
