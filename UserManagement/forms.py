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


class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Das alte Passwort ist falsch.")
        return old_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Die beiden Passwörter stimmen nicht überein.")
        return new_password2

class DeleteUserForm(forms.Form):
    confirm = forms.BooleanField(required=True, label='Profil löschen bestätigen')

