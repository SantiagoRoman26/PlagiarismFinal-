from django import forms

class FormularioAutorizacion(forms.Form):
    opciones = [('autorizar', 'Autorizar'), ('rechazar', 'Rechazar')]
    seleccion = forms.ChoiceField(widget=forms.RadioSelect, choices=opciones, required=True)