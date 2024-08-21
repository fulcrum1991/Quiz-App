from django import forms
from .models import QuizPool,QuizTask,Answer

class QuizPoolForm(forms.ModelForm):
    class Meta:
        model = QuizPool
        fields = ['name']
class QuizTaskForm(forms.ModelForm):
    class Meta:
        model = QuizTask
        fields = ['question']

class AnswerForm(forms.ModelForm):
    correct = forms.ChoiceField(choices=[('True', True), ('False', False)], widget=forms.CheckboxInput)
    class Meta:
        model = Answer
        fields = ['answer','correct',]


