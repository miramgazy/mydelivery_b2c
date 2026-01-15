from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User

class CustomUserChangeForm(UserChangeForm):
    new_password = forms.CharField(
        label='Новый пароль',
        required=False,
        widget=forms.PasswordInput,
        help_text='Оставьте пустым, если не хотите менять пароль.'
    )

    class Meta(UserChangeForm.Meta):
        model = User
