from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import FormularioLogin, FormularioRegistrar, FormularioRol
from django.contrib.auth.models import Group, User
from modelo.models import Usuario, Estudiante, Docente
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from formtools.wizard.views import SessionWizardView
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from correo.views import emailRecuperacion
import random
import string

# Create your views here.
def autenticar(request):
    if request.method == 'POST':
        formulario = FormularioLogin(request.POST)
        if formulario.is_valid():
            usuario = request.POST['username']
            clave = request.POST['password']
            user = authenticate(username = usuario, password=clave)
            # if FailedAttempt.objects.filter(username = usuario).exists():
            #     control=FailedAttempt.objects.get(username=usuario) 
            #     numFallos=control.failures
            # else:
            #     numFallos = 0
            # if numFallos < 5:
            if user is not None:
                if user.is_active:
                    usuario = Usuario.objects.get(correo=user.email)
                    if usuario.estado:                         
                        login(request, user)
                        next_url = request.GET.get('next')  # Obtener la URL a la que se intentó acceder
                        if next_url:
                            return HttpResponseRedirect(next_url)
                        else:
                            return HttpResponseRedirect(reverse('homepage'))
                    else:
                        return HttpResponseRedirect(reverse('no_activo'))
                else:    
                    return HttpResponseRedirect(reverse('no_activo'))
            else:
                messages.add_message(request, messages.INFO, 'Usuario o Clave incorrectas')
            # else:
            #     messages.add_message(request, messages.INFO, 'Demasiados intentos fallidos. Cuenta bloqueada')
        
    else:    
        formulario = FormularioLogin()
    context = {
        'formulario': formulario
    }
    return render (request, 'login/login.html', context) 

def desautenticar(request):
    logout(request)
    return render (request, 'login/logout.html')

def recuperar_contraseña(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        url = request.build_absolute_uri(reverse('autenticar'))
        # Generar una contraseña aleatoria
        nueva_contraseña = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        try:
            # Obtener el usuario por su correo electrónico
            user = User.objects.get(email=correo)
            
            # Cambiar la contraseña del usuario
            user.set_password(nueva_contraseña)
            user.save()
            
            # Enviar la nueva contraseña al correo electrónico del usuario
            emailRecuperacion(correo, nueva_contraseña, url)
            
            return render(request, 'login/recuperacion_exitosa.html')
        
        except User.DoesNotExist:
            print('Usuario no encontrado')
    
    return render(request, 'login/recuperar_contraseña.html')

def emailAutorizacion(User_mail, User_nombre, Admin_Email, Admin_nombre, url):
    context = { 
        'user_mail' : User_mail,
        'user_nombre' : User_nombre,
        'url' : url,
        'admin' : Admin_nombre
               }
    template = get_template('correo/Autorizacion.html')
    content = template.render(context)
    email = EmailMultiAlternatives(
        'Registro de docente',
        'Nuevo Registro',
        settings.EMAIL_HOST_USER,
        [Admin_Email] #todos los destinatarios a quien enviarlos
        #cc= [] #envio de una copia
    )
    email.attach_alternative(content, 'text/html')
    email.send()
    print ('Correo Enviado!')





# Wizard para registrarse y solicitar un rol

TEMPLATES = {
        "registro": 'login/registrar.html',
        "rol": 'autorizar/solicitarRol.html',
    }
class RegistrarWizardView(SessionWizardView):
    form_list = [
        ("registro", FormularioRegistrar),
        ("rol", FormularioRol),
    ]
    
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]
    
    def done(self, form_list, **kwargs):

        formulario_registro_data = self.get_cleaned_data_for_step("registro")
        
        formulario_rol_data = self.get_cleaned_data_for_step("rol")
        # Procesar formulario de registro
        usuario = formulario_registro_data['username']
        clave = formulario_registro_data['password']
        correo = formulario_registro_data['email']
        nombres = formulario_registro_data['first_name']
        apellidos = formulario_registro_data['last_name']

        user = User.objects.create_user(usuario, correo, clave)
        user.last_name = apellidos
        user.first_name = nombres
        user.save()

        usuario_model = Usuario()
        usuario_model.apellidos = apellidos
        usuario_model.nombres = nombres
        usuario_model.correo = correo
        usuario_model.estado = False
        usuario_model.save()

        # Procesar formulario de rol
        rol = formulario_rol_data['rol']
        if rol == 'estudiante':
            usuario_model.save()
            nombre = usuario_model.nombres + ' ' + usuario_model.apellidos
            usuarios = User.objects.all()
            current_site = get_current_site(self.request)
            for usuarioAdmin in usuarios:
                if usuarioAdmin.is_superuser:
                    url = self.request.build_absolute_uri(reverse('activar', args=[usuario_model.usuario_id]))
                    emailAutorizacion(usuario_model.correo, nombre, usuarioAdmin.email, usuarioAdmin.first_name, url)
            pass

        elif rol == 'docente':
            usuario_model.autorizado = True
            usuario_model.save()
            nombre = usuario_model.nombres + ' ' + usuario_model.apellidos
            usuarios = User.objects.all()
            current_site = get_current_site(self.request)
            for usuarioAdmin in usuarios:
                if usuarioAdmin.is_superuser:
                    url = self.request.build_absolute_uri(reverse('activar', args=[usuario_model.usuario_id]))
                    emailAutorizacion(usuario_model.correo, nombre, usuarioAdmin.email, usuarioAdmin.first_name, url)
            pass

        else:
            estudiante_model = Estudiante()
            estudiante_model.usuario = usuario_model
            estudiante_model.save()
        
        return HttpResponseRedirect(reverse('completado'))
        # return HttpResponseRedirect(reverse('autenticar'))
    

# def registrar (request):
#     if request.method == 'POST':
#         formulario = FormularioRegistrar(request.POST)
#         if formulario.is_valid():
#             usuario = request.POST['username']
#             clave = request.POST['password']    
#             correo = request.POST['email']
#             nombres = request.POST['first_name']
#             apellidos = request.POST['last_name']
#             if User.objects.filter(username=usuario).exists():
#                 messages.add_message(request, messages.INFO, 'Username is already in use.')
#                 return redirect(registrar)
#             else:
#                 if User.objects.filter(email=correo).exists():
#                     messages.add_message(request, messages.INFO, 'email is already in use.')
#                     return redirect(registrar)
#                 user = User.objects.create_user(usuario,correo,clave)
#                 user.last_name=apellidos
#                 user.first_name=nombres
#                 #cliente=Group.objects.get(name='cliente')
#                 #user.groups.add(cliente)
#                 user.save()

#                 usuario = Usuario()
#                 usuario.apellidos=apellidos
#                 usuario.nombres=nombres
#                 usuario.correo=correo
#                 usuario.save()
#         else:
#             messages.error(request, 'Registration Failed')
#             return redirect(registrar)
#         return HttpResponseRedirect(reverse('solicitar_rol',args=[usuario.usuario_id]))
#     else:    
#         formulario = FormularioRegistrar()
        
#     context = {
#         'formulario': formulario
#     }
#     return render(request, 'login/registrar.html', context)  

def passwordChange(request):
    if request.method == 'POST':
        formulario = PasswordChangeForm(request.user, request.POST)
        if formulario.is_valid():
            user = formulario.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Tu contraseña fue actualizada!')
            return HttpResponseRedirect(reverse('homepage'))
        else:
            messages.error(request, 'Corrige los errores.')
    else:
        formulario = PasswordChangeForm(request.user)

    context = {
        'formulario': formulario
    }
    return render(request, 'login/passwordChange.html', context)    

def welcome (request):
    return (request, 'login/welcome.html')

def forbidden (request):
    return (request, 'login/forbidden.html') 

def desactivado (request):
    return render(request, 'login/deactive.html')  
def completado (request):
    return render(request, 'login/registro_completado.html')  

