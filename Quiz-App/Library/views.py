from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods

from .forms import QuizPoolForm, QuizTaskForm
from .models import QuizPool, QuizTask, Answer



# Create your views here.

## QuizPools
def library(request):
    quizpools = QuizPool.objects.all()
    return render(request, 'library/library.html', {'quizpools': quizpools})

def get_quizpools(request):
    quizpools = QuizPool.objects.all()
    return render(request, 'library/list_quizpools.html', {'quizpools': quizpools})

def delete_pool(request, id):
    QuizPool.objects.get(id=id).delete()
    quizpools = QuizPool.objects.all()
    return render(request, 'library/list_quizpools.html', {'quizpools': quizpools})

#@permission_required("Library.add_quiztask", login_url='/login', raise_exception=True)
def create_quizpool(request):
    if request.method == 'POST':
        form = QuizPoolForm(request.POST)

        if form.is_valid():
            quizpool = form.save(commit=False)
            quizpool.creator = request.user
            quizpool.save()
    quizpools = QuizPool.objects.all()
    return render(request, 'library/list_quizpools.html', {'quizpools': quizpools})

## QuizTasks
def get_quiztasks(request, pool_id):

    quiztasks = QuizTask.objects.filter(pool_id=pool_id)
    print(quiztasks)
    return render(request, 'library/list_quiztasks.html', {'quiztasks': quiztasks})

def delete_task(request, pool_id):
    QuizTask.objects.get(id=id).delete()
    quiztasks = QuizTask.objects.get(id=pool_id)
    return render(request, 'library/list_quizpools.html', {'quiztasks': quiztasks})

#@permission_required("Library.add_quiztask", login_url='/login', raise_exception=True)
def create_quiztask(request):
    if request.method == 'POST':
        form = QuizPoolForm(request.POST)

        if form.is_valid():
            quizpool = form.save(commit=False)
            quizpool.creator = request.user
            quizpool.save()
    quizpools = QuizPool.objects.all()
    return render(request, 'library/list_quizpools.html', {'quizpools': quizpools})

def get_answers(request):
    answers = Answer.objects.all()
    return render(request, 'library/list_answers.html', {'answers': answers})

