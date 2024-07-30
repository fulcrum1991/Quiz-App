from django import forms
from .models import QuizTask


class QuizTaskForm(forms.ModelForm):
    class Meta:
        model = QuizTask
        fields = ['question']

