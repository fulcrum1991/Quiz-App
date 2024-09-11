
# Create your models here.
# models.py

from django.contrib.auth.models import User
from django.db import models
from Library.models import QuizPool, QuizTask, Answer

class MPGame(models.Model):
    name = models.CharField(max_length=255)
    pool = models.ForeignKey(QuizPool, on_delete=models.CASCADE)
    player1 = models.ForeignKey(User, related_name='player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name='player2', on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def is_full(self):
        return self.player2 is not None

class MPGame_contains_Quiztask(models.Model):
    game = models.ForeignKey(MPGame, on_delete=models.CASCADE)
    task = models.ForeignKey(QuizTask, on_delete=models.SET_NULL, null=True)      # check CASCADE
    player1_answer = models.ForeignKey(Answer, related_name='player1_answer', null=True, blank=True, on_delete=models.SET_NULL)
    player2_answer = models.ForeignKey(Answer, related_name='player2_answer', null=True, blank=True, on_delete=models.SET_NULL)
    current_turn = models.ForeignKey(User, related_name='current_turn', on_delete=models.CASCADE)
    correct_answered = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    current_turn = models.ForeignKey(User, on_delete=models.CASCADE)  # Bezug auf User für current_turn