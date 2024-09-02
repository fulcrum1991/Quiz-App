from django.contrib.auth.models import User
from django.db import models
from Library.models import QuizPool
from Library.models import QuizTask


# Create your models here.
class QuizSession(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.hosted_quiz_pool = None

    code = models.CharField(max_length=6, unique=True)
    host = models.ForeignKey(User, related_name='hosted_sessions', on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='participating_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class Question(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.number = None

    quiz_pool = models.ForeignKey('Library.QuizPool', on_delete=models.CASCADE)


class Answer(models.Model):
    text = models.TextField()
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)


class PlayerAnswer(models.Model):
    session = models.ForeignKey(QuizSession, related_name='player_answers', on_delete=models.CASCADE)
    player = models.ForeignKey(User, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
