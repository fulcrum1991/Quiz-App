from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class QuizPool(models.Model):
    name = models.CharField(max_length=250)
    creator = models.ForeignKey(User, default='1', on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

class QuizTask(models.Model):
    pool = models.ForeignKey(QuizPool, default='1', on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    approved = models.BooleanField(default=False)
    creator = models.ForeignKey(User, default='1', on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class Answer(models.Model):
    task = models.ForeignKey(QuizTask, default='1', on_delete=models.CASCADE)
    creator = models.ForeignKey(User, default='1', on_delete=models.SET_NULL, null=True)
    answer = models.CharField(max_length=500)
    correct = models.BooleanField(default=False)
    explanation = models.CharField(max_length=500)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

