from django.shortcuts import render
from modelo.models import Usuario, Estudiante, Docente
from .forms import FormularioUsuario,FormularioRol
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.db.models.deletion import ProtectedError  
from django.db.models import Q 
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

def verificarRolAnterior(usuario_id):
    usuario = Usuario.objects.get(usuario_id=usuario_id)
    user = User.objects.get(email = usuario.correo)
    if user.groups.filter(name = "estudiante").exists():
        estudiante = Estudiante.objects.get(usuario = usuario)
        return 1, estudiante.estudiante_id
    elif user.groups.filter(name = "docente").exists():
        docente = Docente.objects.get(usuario = usuario)
        return 2, docente.docente_id
    elif user.groups.filter(name = "admin").exists():
        return 3, None
    else:
        return 0, None

@login_required
def index(request):
    user = request.user
    usuarioGuardado = User.objects.get(email = user.email)
    cond = usuarioGuardado.first_name.strip() # valor de la variable first_name
    cond = not cond # mandar true si esta vacio 
    if user.groups.filter(name = "admin").exists():
        message = request.GET.get('message')
        Usuarios = Usuario.objects.all() 
        listaUsuarios = [
            {**usuario.__dict__, 'userU': User.objects.get(email=usuario.correo)}
            for usuario in Usuarios
        ] 
        busqueda = request.POST.get("busqueda")     
        if busqueda:
            listaUsuarios = Usuario.objects.filter(
                Q(apellidos__icontains = busqueda) | 
                Q(nombres__icontains = busqueda) 
            ).distinct() 
        return render (request, 'usuarios/index_Todos.html', locals())
    else:
        return render(request, 'login/forbidden.html', locals()) 


@login_required
def autorizaciones(request):
    user = request.user
    if user.groups.filter(name = "admin").exists():
        listaUsuarios = Usuario.objects.filter(estado = False)
        busqueda = request.POST.get("busqueda")     
        if busqueda:
            listaUsuarios = Usuario.objects.filter(
                Q(apellidos__icontains = busqueda) | 
                Q(nombres__icontains = busqueda) 
            ).distinct() 
        return render (request, 'usuarios/index.html', locals())
    else:
        return render(request, 'login/forbidden.html', locals()) 

@login_required
def eliminarUsuario(request, usuario_id):
    user = request.user
    usuario = Usuario.objects.get(usuario_id=usuario_id)
    if user.groups.filter(name = "admin").exists():
        try:
            rolAnterior,idRol = verificarRolAnterior(usuario_id)
            user = User.objects.get(email = usuario.correo)
            if rolAnterior == 2:
                docente_grupo=Group.objects.get(name='docente')
                docente = Docente.objects.get(docente_id = idRol)
                docente.delete()
                user.groups.remove(docente_grupo)
            elif rolAnterior == 3:
                user.is_staff = False
                user.is_superuser = False
                admin_grupo=Group.objects.get(name='admin')
                user.groups.remove(admin_grupo)
            elif rolAnterior == 1:
                estudiante = Estudiante.objects.get(estudiante_id = idRol)
                estudiante_grupo=Group.objects.get(name='estudiante')
                user.groups.remove(estudiante_grupo)
                estudiante.delete()
            else :
                messages.error(request, 'Usuario '+ usuario.nombres +' no tiene un rol anterior, por ende no se puede eliminar correctamente')
            usuario = Usuario.objects.get(usuario_id=usuario_id)
            messages.success(request, 'Usuario '+ usuario.nombres +' eliminado')
            user.delete()
            usuario.delete()
            return redirect(index)
        except ProtectedError as e:
            # Manejo del error
            registros_asociados = e.protected_objects
            message = f"No se puede eliminar el Docente debido a registros asociados en GestionDocumentos: {registros_asociados}"
            messages.success(request, message)
            url = reverse('usuarios') + f'?message={message}'
            return redirect(url)
            
    else:
        return render(request, 'login/forbidden.html', locals())

@login_required
def modificarUsuario(request, usuario_id):
    user = request.user
    usuario = Usuario.objects.get(correo=user.email)
    if user.groups.filter(name = "admin").exists():
        usuario = Usuario.objects.get(usuario_id=usuario_id)
        if request.method == 'GET':
            formulario_usuario = FormularioUsuario(instance = usuario)
        else:
            userU = User.objects.get(email = usuario.correo)
            formulario_usuario = FormularioUsuario(request.POST, instance = usuario)
            if formulario_usuario.is_valid():

                nuevo_correo = request.POST.get('correo')
                
                # Verifica si el nuevo correo ya existe en otro usuario
                
                # Si el correo no existe en otros usuarios, guarda los cambios
                formulario_usuario.save()
                
                # Actualiza los campos en el objeto User
                userU.first_name = usuario.nombres
                userU.last_name = usuario.apellidos
                userU.email = nuevo_correo
                userU.save()
                messages.success(request, 'Usuario '+ usuario.nombres +' editado')
                # userU.first_name 
            else:
                for field_name, error_messages in formulario_usuario.errors.items():
                    for error_message in error_messages:
                        messages.error(request, f'Error en el campo {formulario_usuario.fields[field_name].label}: {error_message}')
                return render (request, 'usuarios/modificar.html', locals())
            return redirect(index)
        return render (request, 'usuarios/modificar.html', locals())
    else:
        return render(request, 'login/forbidden.html', locals())

@login_required
def cambiarRolUsuario(request, usuario_id): 
    user = request.user
    if user.groups.filter(name = "admin").exists():
        usuario = Usuario.objects.get(usuario_id=usuario_id)
        user = User.objects.get(email = usuario.correo)
        formulario_rol = FormularioRol(request.POST)
        if request.method == 'POST':
            if formulario_rol.is_valid():
                #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                    formulario_rol_data = formulario_rol.cleaned_data
                    rol = formulario_rol_data['rol']
                    rolAnterior,idRol = verificarRolAnterior(usuario.usuario_id)
                    if rol == 'estudiante' and rolAnterior !=1:
                        if rolAnterior == 2:
                            try:
                                docente = Docente.objects.get(docente_id = idRol)
                                docente.delete()
                                estudiante = Estudiante()
                                estudiante.usuario = usuario
                                estudiante.save()
                                docente_grupo=Group.objects.get(name='docente')
                                user.groups.remove(docente_grupo)
                            except ProtectedError as e:
                                # Manejo del error
                                registros_asociados = e.protected_objects
                                message = f"No se puede eliminar el Docente debido a registros asociados en GestionDocumentos: {registros_asociados}"
                                url = reverse('usuarios') + f'?message={message}'
                                return redirect(url)
                        elif rolAnterior == 3:
                            user.is_staff = False
                            user.is_superuser = False
                            admin_grupo=Group.objects.get(name='admin')
                            user.groups.remove(admin_grupo)
                        nuevo_grupo = Group.objects.get(name='estudiante')
                        user.groups.add(nuevo_grupo)
                    elif rol == 'docente' and rolAnterior !=2:
                        if rolAnterior == 1:
                            estudiante = Estudiante.objects.get(estudiante_id = idRol)
                            estudiante.delete()
                            docente = Docente()
                            docente.usuario = usuario
                            docente.save()
                            estudiante_grupo=Group.objects.get(name='estudiante')
                            user.groups.remove(estudiante_grupo)
                            
                        elif rolAnterior == 3:
                            user.is_staff = False
                            user.is_superuser = False
                            admin_grupo=Group.objects.get(name='admin')
                            user.groups.remove(admin_grupo)
                        nuevo_grupo = Group.objects.get(name='docente')
                        user.groups.add(nuevo_grupo)
                    elif rol == 'admin' and rolAnterior !=3:
                        if rolAnterior == 1:
                            estudiante = Estudiante.objects.get(estudiante_id = idRol)
                            estudiante.delete()
                            docente = Docente()
                            docente.usuario = usuario
                            docente.save()
                            estudiante_grupo=Group.objects.get(name='estudiante')
                            user.groups.remove(estudiante_grupo)
                        elif rolAnterior == 2:
                            try:
                                docente = Docente.objects.get(docente_id = idRol)
                                docente.delete()
                                estudiante = Estudiante()
                                estudiante.usuario = usuario
                                estudiante.save()
                                docente_grupo=Group.objects.get(name='docente')
                                user.groups.remove(docente_grupo)
                            except ProtectedError as e:
                                # Manejo del error
                                registros_asociados = e.protected_objects
                                message = f"No se puede eliminar el Docente debido a registros asociados en GestionDocumentos: {registros_asociados}"
                                url = reverse('usuarios') + f'?message={message}'
                                return redirect(url)
                        nuevo_grupo = Group.objects.get(name='admin')
                        user.groups.add(nuevo_grupo)
                    else:
                        print("error al usar el boton o de rol repetido")
                        message=("error rol repetido.")
                        url = reverse('usuarios') + f'?message={message}'
                        return redirect(url)
                    message=("rol cambiado con exito")
                    url = reverse('usuarios') + f'?message={message}'
                    return redirect(url)
            #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            message=("error en el formulario")
            url = reverse('usuarios') + f'?message={message}'
            return redirect(url)
        return render (request, 'usuarios/rol.html', locals())
    else:
        return render(request, 'login/forbidden.html', locals())

@login_required
def generarUsuario(request):
    user = request.user
    formulario_usuario = FormularioUsuario(request.POST)
    if request.method == 'POST':
        if formulario_usuario.is_valid():
            usuario = Usuario()
            datos_usuario = formulario_usuario.cleaned_data
            usuario.apellidos= datos_usuario.get('apellidos')
            usuario.nombres= datos_usuario.get('nombres')
            usuario.correo= user.email
            usuarioGuardado = User.objects.get(email = user.email)
            usuarioGuardado.first_name = usuario.nombres
            usuarioGuardado.last_name = usuario.apellidos
            
                #ORM
            usuario.save()
            usuarioGuardado.save()
        return redirect(index)
    return render (request, 'usuarios/crear.html', locals())
    