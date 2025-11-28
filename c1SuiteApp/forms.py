from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuário')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

class UsuarioForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'perfil', 'senha', 'ativo']
 