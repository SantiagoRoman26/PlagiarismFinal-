from django import forms
from modelo.models import Usuario
class FormularioUsuario(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["apellidos","nombres","correo"]

class FormularioRol(forms.Form):
    rol = forms.ChoiceField(choices=[('estudiante', 'Estudiante'), ('docente', 'Docente'), ('admin', 'Administrador')], widget=forms.HiddenInput)