from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import QuizTask


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class QuizTaskForm(forms.ModelForm):
    class Meta:
        model = QuizTask
        fields = ['question']

