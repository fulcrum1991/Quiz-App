from django import forms
from .models import QuizPool, QuizTask

class QuizPoolForm(forms.ModelForm):
    class Meta:
        model = QuizPool
        fields = ['name']
class QuizTaskForm(forms.ModelForm):
    class Meta:
        model = QuizTask
        fields = ['question']
