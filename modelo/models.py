from django.db import models
import os

class Usuario(models.Model):
    usuario_id = models.AutoField(primary_key = True)
    nombres = models.CharField(max_length = 70, null = False)
    apellidos = models.CharField(max_length = 70, null = False)
    correo = models.EmailField(max_length = 105, null = False, unique = True)
    date_created = models.DateTimeField(auto_now_add = True)
    autorizado = models.BooleanField(default = False)
    estado = models.BooleanField(default = True) # en el caso de que un alumno se retire, su estado pasara a false hasta decidir si se eliminara o no 

    def __int__(self):   
        return self.usuario_id

class Estudiante(models.Model):
    estudiante_id = models.AutoField(primary_key = True)
    usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)


    def __int__(self):   
        return self.estudiante_id

class Docente(models.Model):
    docente_id = models.AutoField(primary_key = True)
    usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)

    def __int__(self):   
        return self.docente_id

class Documento(models.Model):
    documento_id = models.AutoField(primary_key = True)
    archivo= models.FileField(upload_to='pdfs/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    # usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)
    tipo = models.CharField(max_length=50, default='pdf')
    estado = models.BooleanField(default = True) # el estado representa si se lo toma en cuenta para la busqueda de plagio en ese documento. 
    visible = models.BooleanField(default = False) # el unico documento con estado true sera el ultimo documento subido por el usuario. o solo un documento para su analisis, para seguridad
    

    def __int__(self):   
        return self.documento_id
    
    def get_nombre_archivo(self):
        return os.path.basename(self.archivo.name)

class GestionDocumentos(models.Model):
    gestion_id = models.AutoField(primary_key = True)
    estudiante = models.ForeignKey(Estudiante, null = True, blank = True, on_delete = models.SET_NULL)
    docente = models.ForeignKey(Docente, null = True, blank = True, on_delete = models.PROTECT)                                 #el campo esta protegido se deben elminar todos los resultados o Gestiones relacionados al docente 
    documento = models.ForeignKey(Documento, on_delete = models.CASCADE)
    titulo= models.CharField(max_length = 70, null = True, default= "")
    comentario= models.CharField(max_length = 70, null = True, default= "")

    def __int__(self):   
        return self.gestion_id
    
class Resultado(models.Model):
    resultado_id = models.AutoField(primary_key = True)
    archivo= models.FileField(upload_to='resultados/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    ejecutando = models.BooleanField(default = False)
    management = models.ForeignKey(GestionDocumentos, on_delete=models.CASCADE)
    estado = models.BooleanField(default = False) # el unico documento con estado true sera el ultimo documento subido por el usuario. o solo un documento para su analisis, para seguridad
    plagio = models.JSONField(default=list)
    informacion = models.JSONField(default=dict)


    def __int__(self):   
        return self.resultado_id