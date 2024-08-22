from django.db import models
from django.contrib.auth.models import User
from Library.models import QuizTask

# Create your models here.
class Quiz(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed_at = models.DateTimeField()

class Quiz_contains_Quiztask(models.Model):
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)          # check
    task_id = models.ForeignKey(QuizTask, on_delete=models.CASCADE)      # check
    correct_answered = models.BooleanField()
    completed = models.BooleanField()