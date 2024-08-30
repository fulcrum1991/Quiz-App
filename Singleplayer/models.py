from django.db import models
from django.contrib.auth.models import User
from Library.models import QuizPool, QuizTask, Answer

# Create your models here.
class SPGame(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pool = models.ForeignKey(QuizPool, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(blank=True, null=True)

class SPGame_contains_Quiztask(models.Model):
    game = models.ForeignKey(SPGame, on_delete=models.CASCADE)        # check CASCADE
    task = models.ForeignKey(QuizTask, on_delete=models.SET_NULL, null=True)      # check CASCADE
    selected_answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True) # check CASCADE
    correct_answered = models.BooleanField(blank=True, null=True)
    completed = models.BooleanField(default=False)

