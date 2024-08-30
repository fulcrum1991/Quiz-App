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
    # Rückgabe:
    return render(request, 'singleplayer/sp_overview.html')

def sp_new_game(request):
    # Rückgabe: Rendert die Seite zum Start eines neuen Spiels (sp_new_game.html).
    # Zusätzlich wird get_library_content() ausgeführt, um der Seite Quizpools und -Tasks
    # für die Darstellung zu übergeben

    return render(request, 'singleplayer/sp_new_game.html',
                  get_library_content())

def show_lib_content(request, pool_id=None):
    # Rückgabe:
    selected_pool = None
    if bool(pool_id):
        selected_pool = QuizPool.objects.get(id=pool_id)

    return render(request, 'singleplayer/sp_new_game_content.html',
                  get_library_content(selected_pool=selected_pool))



def sp_resume_game(request):
    # Rückgabe: Rendert die vollständige Bibliothek (library.html)
    return render(request, 'singleplayer/sp_resume_game.html')

def sp_history(request):
    # Rückgabe:
    return render(request, 'singleplayer/sp_history.html')


# Game
def get_questions_by_game(sp_game):
    # Erstellt eine Liste von Dictionaries. Jedes Element (Dictionary) enhählt Informationen zu einer Quiztask, bestehend aus
    # task.id, der question und dem Status, ob diese Quiztask bereits richtig beantwortet wurde.
    # Rückgabe: Diese Liste
    questions_status_list = []

    tasks_by_game = SPGame_contains_Quiztask.objects.filter(game=sp_game)

    for task in tasks_by_game:
        questions_status_list.append({'task_id': task.id,
                                      'question': QuizTask.objects.get(id=task.task_id).question,
                                      'correct_answered': task.correct_answered})

    return questions_status_list

def get_quiztask_answers(task_id):
    # Erfragt Quiztask-Objekt und die dazugehörigen Answer-Objekte.
    # Rückgabe: Dictionary bestehend aus einem Quiztask-Objekt und den dazugehörigen Answer-Objekten
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


def render_game_card(request, game_id, task_id, action, selected_answer_id=None):
    current_game = SPGame.objects.get(id=game_id)
    quiztasks = SPGame_contains_Quiztask.objects.filter(game=current_game)
    result = None

    # Reaktion auf Navigationsbutton 'Weiter' und 'Zurück'
    if action == 'next':
        task_id = get_next_task(task_id, quiztasks)
    elif action == 'previous':
        task_id = get_previous_task(task_id, quiztasks)
    elif action == 'select_answer':
        pass

    quiztask_answers = get_quiztask_answers(task_id)

    current_task = quiztasks.get(task_id=task_id)
    if current_task.completed == True:
        result = get_evaluation_result(current_task.correct_answered)
        selected_answer_id = current_task.selected_answer_id

    return render(request, 'singleplayer/game_card.html',
                  {'sp_game': current_game,
                   'quiztask_answers': quiztask_answers,
                   'selected_answer_id': selected_answer_id,
                   'result': result
                   })

def evaluate_task(request, game_id, task_id, selected_answer_id):
    current_game = SPGame.objects.get(id=game_id)
    selected_answer = Answer.objects.get(id=selected_answer_id)
    result = None

    if selected_answer.correct == True:
        sp_game_quiztask = SPGame_contains_Quiztask.objects.get(game_id=game_id,task_id=task_id)
        sp_game_quiztask.selected_answer = Answer.objects.get(id=selected_answer_id)
        sp_game_quiztask.correct_answered = True
        sp_game_quiztask.completed = True
        sp_game_quiztask.save()

        result = get_evaluation_result(True)

    else:
        sp_game_quiztask = SPGame_contains_Quiztask.objects.get(game_id=game_id,task_id=task_id)
        sp_game_quiztask.selected_answer = Answer.objects.get(id=selected_answer_id)
        sp_game_quiztask.correct_answered = False
        sp_game_quiztask.completed = True
        sp_game_quiztask.save()

        result = get_evaluation_result(False)

    quiztask_answers = get_quiztask_answers(task_id)

    # Prüfen, ob alle Aufgaben beantwortet wurden
    game_completed = check_game_completed(game=current_game)
    if game_completed:
        current_game.completed_at=dt.datetime.now()
        current_game.save()


    return render(request, 'singleplayer/game_card.html',
                  {'sp_game': current_game,
                   'quiztask_answers': quiztask_answers,
                   'selected_answer_id': selected_answer_id,
                   'result': result
                   })


# Hilfsfunktionen
def get_next_task(task_id: int, quiztasks: SPGame_contains_Quiztask):
    flag = False
    new_task_id = None
    for task in quiztasks:
        if flag == True:
            new_task_id = task.task_id
            break
        if task.task_id == task_id:
            flag = True

    return new_task_id


def get_previous_task(task_id: int, quiztasks: SPGame_contains_Quiztask):
    flag = False
    new_task_id = quiztasks.first().id
    for task in quiztasks:
        if task.task_id != task_id:
            new_task_id = task.task_id
        else:
            break

    return new_task_id

def get_evaluation_result(correct_answered: bool):
    result = {'correct_answered': correct_answered, 'answer_message': ''}

    if correct_answered:
        result['answer_message'] = 'Die Antwort ist richtig.'
    else:
        result['answer_message'] = 'Die Antwort ist falsch.'

    return result

def check_game_completed(game: SPGame):
    unfinished_tasks = SPGame_contains_Quiztask.objects.filter(game=game, completed=False)
    if unfinished_tasks.__len__() == 0:
        return True
    else:
        return False