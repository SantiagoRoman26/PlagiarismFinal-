import re
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
        
class FormularioRegistrar(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput(), help_text=password_validation.password_validators_help_text_html(password_validation.get_default_password_validators()))
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirmar contraseña")
    email = forms.EmailField(max_length=105)
    first_name = forms.CharField(max_length=70)
    last_name = forms.CharField(max_length=70)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username is already in use.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email is already in use.')
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise ValidationError("Passwords don't match.")
        return confirm_password
    
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data['password']

        # Validate password using Django's password validators
        try:
            password_validation.validate_password(password, None)
        except ValidationError as e:
            self.add_error('password', e.messages[0])

        # Validate password using custom validators
        errors = {}
        if not re.search(r'[0-9]', password):
            errors['password'] = _('La contraseña debe contener almenos un número.')

        if not re.search(r'[a-zA-Z]', password):
            errors['password'] = _('La contraseña debe contener almenos una letra.')

        if not re.search(r'[~!@#$%^&*()_+-=\/\[\]{}|;:,<.>?"]', password):
            errors['password'] = [_('La contraseña debe contener almenos un caracter especial.')]

        if errors:
            for field, error in errors.items():
                self.add_error(field, error)

        return cleaned_data

class FormularioRol(forms.Form):
    rol = forms.ChoiceField(choices=[('estudiante', 'Estudiante'), ('docente', 'Docente')], widget=forms.HiddenInput)

class FormularioLogin(forms.Form):
    username= forms.CharField()
    password= forms.CharField(widget=forms.PasswordInput()) 

class CambiarPassword(forms.Form):
    oldPassword = forms.CharField(widget=forms.PasswordInput())
    password = forms.CharField(widget=forms.PasswordInput,
                               help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    def clean(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password2'):
            raise forms.ValidationError('Passwords are not equal')
        password_validation.validate_password(self.cleaned_data.get('password'), None)
        return self.cleaned_data