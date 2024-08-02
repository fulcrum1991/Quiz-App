from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import QuizTask


class QuizTaskForm(forms.ModelForm):
    class Meta:
        model = QuizTask
        fields = ['question']
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    role = forms.ChoiceField(choices=[('student', 'Student'), ('dozent', 'Dozent')], widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')
