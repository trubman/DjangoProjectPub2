from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя',
        # help_text='Максимум 150 символов',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        }),
    )
    password = forms.CharField(
        label='Пароль',
        # help_text='Максимум 150 символов',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        }),
    )