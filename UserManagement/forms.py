from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.db import models


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    role = forms.ChoiceField(choices=[('student', 'Student'), ('dozent', 'Dozent')], widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

from django.contrib.auth.forms import PasswordChangeForm

class CustomPasswordChangeForm(PasswordChangeForm):
    pass


class DeleteUserForm(forms.Form):
    confirm = forms.BooleanField(required=True, label='Profil löschen bestätigen')

