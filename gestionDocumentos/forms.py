from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class FormularioGestion(forms.Form):
    titulo= forms.CharField(max_length = 70)
    comentario= forms.CharField(max_length = 70)
    email = forms.EmailField(max_length = 105)