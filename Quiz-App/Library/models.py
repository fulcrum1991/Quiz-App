from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class QuizTask(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)      # on_delete=models.CASCADE = wenn ein Nutzer gelöscht wird, werden auch seine Posts gelöscht
    question = models.CharField(max_length=100)
    # answers
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
    # convert obj to string
        return self.question + "\n" +self.author