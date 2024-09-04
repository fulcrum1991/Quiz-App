import datetime

from django.db import models
from django.contrib.auth.models import User
from Library.models import QuizPool, QuizTask, Answer

# Create your models here.
class SPGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pool = models.ForeignKey(QuizPool, on_delete=models.CASCADE)
    name = models.CharField(max_length=350)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    completed = models.BooleanField(blank=True, default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    correct_percent = models.FloatField(default=0)

class SPGame_contains_Quiztask(models.Model):
    game = models.ForeignKey(SPGame, on_delete=models.CASCADE)        # check CASCADE
    task = models.ForeignKey(QuizTask, on_delete=models.CASCADE)      # check CASCADE
    selected_answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True) # check CASCADE
    correct_answered = models.BooleanField(blank=True, null=True)
    completed = models.BooleanField(default=False)

