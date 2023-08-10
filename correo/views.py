from django.shortcuts import render
import os
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
# Create your views here.

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
        'Registro Completado y autorizado',
        'Nuevo Registro',
        settings.EMAIL_HOST_USER,
        [Admin_Email] #todos los destinatarios a quien enviarlos
        #cc= [] #envio de una copia
    )
    email.attach_alternative(content, 'text/html')
    email.send()
    print ('Correo Enviado!')

def emailRegistroCompletado(User_mail, User_nombre, url):
    context = { 
        'user_mail' : User_mail,
        'user_nombre' : User_nombre,
        'url' : url,
               }
    template = get_template('correo/cuenta_registrada.html')
    content = template.render(context)
    email = EmailMultiAlternatives(
        'Registro de docente',
        'Nuevo Registro',
        settings.EMAIL_HOST_USER,
        [User_mail] #todos los destinatarios a quien enviarlos
        #cc= [] #envio de una copia
    )
    email.attach_alternative(content, 'text/html')
    email.send()
    print ('Correo Registro Enviado!')

def emailCompartir(correos, comentario, User_nombre, archivo_adjunto):
    context = { 
        'comentario' : comentario,
        'user_nombre' : User_nombre,
                }
    template = get_template('correo/Compartir.html')
    content = template.render(context)
    email = EmailMultiAlternatives(
        'Resultado compartido',
        'Se le ha compartido el siguiente resultado de analisis de plagio',
        settings.EMAIL_HOST_USER,
        correos #todos los destinatarios a quien enviarlos
        #cc= [] #envio de una copia
    )
    email.attach_alternative(content, 'text/html')
    if archivo_adjunto:
        file_path = archivo_adjunto.path
        file_name = os.path.basename(file_path)
        email.attach(file_name, archivo_adjunto.read())

    email.send()
    print ('Correo Compartir Enviado!')

def emailResultado(mail):
    context = { 'mail' : mail }
    template = get_template('correo/proceso_concluido.html')
    content = template.render(context)
    email = EmailMultiAlternatives(
        'Resultado de, analisis',
        'Resultado finalizado',
        settings.EMAIL_HOST_USER,
        [mail] #todos los destinatarios a quien enviarlos
        #cc= [] #envio de una copia
    )
    email.attach_alternative(content, 'text/html')
    email.send()
    print ('Correo Resultado Enviado!')

def emailRecuperacion(User_mail, nuevaContraseña, url):
    context = { 
        'user_mail' : User_mail,
        'nueva_contraseña' : nuevaContraseña,
        'url' : url,
               }
    template = get_template('correo/recuperar_contrasena.html')
    content = template.render(context)
    email = EmailMultiAlternatives(
        'Un correo de prueba',
        'Recuperar contraseña',
        settings.EMAIL_HOST_USER,
        [User_mail] #todos los destinatarios a quien enviarlos
        #cc= [] #envio de una copia
    )
    email.attach_alternative(content, 'text/html')
    email.send()
    print ('Correo de Recuperacion Enviado!')