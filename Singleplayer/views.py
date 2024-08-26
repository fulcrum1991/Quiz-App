from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods

from Library.models import QuizPool, QuizTask, Answer

from Library.views import get_library_content, get_answers
from Singleplayer.models import SPGame, SPGame_contains_Quiztask

# from .forms import QuizPoolForm, QuizTaskForm, AnswerForm
# from .models import QuizPool, QuizTask, Answer

import datetime as dt


# Create your views here.


def sp_overview(request):
    # Rückgabe: Rendert die vollständige Bibliothek (library.html)
    return render(request, 'singleplayer/sp_overview.html')

def sp_new_game(request):
    # Rückgabe: Rendert die vollständige Bibliothek (library.html)

    return render(request, 'singleplayer/sp_new_game.html',
                  get_library_content())

def show_lib_content(request, pool_id=None):
    # Rückgabe: Rendert die vollständige Bibliothek (library.html)
    selected_pool = None
    if bool(pool_id):
        selected_pool = QuizPool.objects.get(id=pool_id)

    return render(request, 'singleplayer/sp_new_game_content.html',
                  get_library_content(selected_pool=selected_pool))



def sp_resume_game(request):
    # Rückgabe: Rendert die vollständige Bibliothek (library.html)
    return render(request, 'singleplayer/sp_resume_game.html')

def sp_history(request):
    # Rückgabe: Rendert die vollständige Bibliothek (library.html)
    return render(request, 'singleplayer/sp_history.html')


## Game
def get_questions_by_game(sp_game):
    questions_status_list = []

    tasks_by_game = SPGame_contains_Quiztask.objects.filter(game=sp_game)

    for task in tasks_by_game:
        questions_status_list.append({'task_id': task.id,
                                      'question': QuizTask.objects.get(id=task.task_id).question,
                                      'correct_answered': task.correct_answered})

    return questions_status_list

def get_quiztask_answers(task_id):
    quiztask = QuizTask.objects.get(id=task_id)
    answers = Answer.objects.filter(task_id=task_id)

    return {'quiztask': quiztask, 'answers': answers}

def create_game(request, pool_id):
    quizpool = QuizPool.objects.get(id=pool_id)
    timestamp = dt.datetime.now()
    # Game Objekt erstellen
    sp_game = SPGame(name=quizpool.name + ' - ' + timestamp.strftime('%d.%m.%Y %H:%M'),
                     user=request.user,
                     pool=quizpool,)
    sp_game.save()

    # SPGame_contains_Quiztask Objekt erstellen und damit Quiztasks dem Game zuordnen
    quiztasks = QuizTask.objects.filter(pool=quizpool)

    for task in quiztasks:
        sp_game_quiztasks = SPGame_contains_Quiztask(
            game=sp_game,
            task=task,)
        sp_game_quiztasks.save()

    # returns
    questions_status_list = get_questions_by_game(sp_game)
    first_quiztask = quiztasks[0]
    quiztask_answers = get_quiztask_answers(first_quiztask.id)


    return render(request, 'singleplayer/sp_game.html',
                  {'sp_game': sp_game,
                   'questions_status_list':  questions_status_list,
                   'quiztask_answers': quiztask_answers,
                   })


def evaluate_task(request):
    return render(request, 'singleplayer/game_card.html')

def previous_task(request, game_id, task_id):
    print(game_id, task_id)
    current_game = SPGame.objects.get(id=game_id)
    quiztasks = SPGame_contains_Quiztask.objects.filter(game=current_game)

    flag = False
    previous_id = quiztasks.first().id
    for task in quiztasks:
        if task.task_id != task_id:
            previous_id = task.task_id
        else:
            break

    quiztask_answers = get_quiztask_answers(previous_id)

    print('next: ' + str(previous_id))
    print(quiztask_answers)

    return render(request, 'singleplayer/game_card.html',
                  {'sp_game': current_game,
                   'quiztask_answers': quiztask_answers,
                   })
def next_task(request, game_id, task_id):
    current_game = SPGame.objects.get(id=game_id)
    quiztasks = SPGame_contains_Quiztask.objects.filter(game=current_game)

    flag = False
    next_id = None
    for task in quiztasks:
        if flag == True:
            next_id = task.task_id
            break
        if task.task_id == task_id:
            flag = True

    quiztask_answers = get_quiztask_answers(next_id)


    print('next: ' + str(next_id))
    print(quiztask_answers)

    return render(request, 'singleplayer/game_card.html',
                  {'sp_game': current_game,
                   'quiztask_answers': quiztask_answers,
                   })


def check_answer(request, game_id, answer_id):
    print(game_id)
    print(answer_id)