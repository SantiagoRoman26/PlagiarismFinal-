from django.contrib import admin
from .models import Usuario
from .models import Estudiante
from .models import Docente
from .models import Documento
from .models import GestionDocumentos
from .models import Resultado


admin.site.register(Usuario)
admin.site.register(Estudiante)
admin.site.register(Docente)
admin.site.register(Documento)
admin.site.register(GestionDocumentos)
admin.site.register(Resultado)
