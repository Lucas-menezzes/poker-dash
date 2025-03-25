from django import forms
from .models import Player
from django.contrib.auth.hashers import make_password

class PlayerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirme a Senha")

    class Meta:
        model = Player
        fields = ['name', 'username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "As senhas não coincidem.")
        
        # Armazenando a senha como hash
        cleaned_data['password'] = make_password(password)
        
        return cleaned_data
