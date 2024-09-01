from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class QuizPool(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, default='1', on_delete=models.SET('1'))      # on_delete=models.SET(1) = absicht uid = 1
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

class QuizTask(models.Model):
    pool = models.ForeignKey(QuizPool, default='1', on_delete=models.CASCADE)       # Wenn Pool gelöscht werden auch die fragen gelöscht
    question = models.CharField(max_length=100)
    approved = models.BooleanField(default=False)
    creator = models.ForeignKey(User, default='1', on_delete=models.SET('1'))  # on_delete=models.SET(1) = absicht uid = 1
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return str(self.question)

class Answer(models.Model):
    task = models.ForeignKey(QuizTask, default='1', on_delete=models.CASCADE)  # Wenn Pool gelöscht werden auch die fragen gelöscht
    creator = models.ForeignKey(User, default='1', on_delete=models.SET('1'))   # on_delete=models.SET(1) = absicht uid = 1
    answer = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)
    explanation = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return str(self.answer + " : " + str(self.correct))