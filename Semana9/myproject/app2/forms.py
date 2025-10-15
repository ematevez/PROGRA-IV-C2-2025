from django import forms

class ClienteForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    email = forms.EmailField()
    foto = forms.ImageField()