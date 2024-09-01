from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods


from Library.models import QuizPool, QuizTask, Answer
from Library.views import get_library_content, get_answers
from Singleplayer.SpHelperFunctions import get_questions_by_game, get_next_task, get_previous_task, \
    get_evaluation_result, check_game_completed, get_game_stats, get_unfinished_games, get_pool_stats, \
    get_finished_games, get_quiztask_answers
from Singleplayer.models import SPGame, SPGame_contains_Quiztask


import datetime as dt


# Create your views here.
@login_required(login_url='/login')
def sp_overview(request):
    # Rückgabe:
    return render(request, 'singleplayer/sp_overview.html')


def sp_new_game(request):
    # Rückgabe: Rendert die Seite zum Start eines neuen Spiels (sp_new_game.html).
    # Zusätzlich wird get_library_content() ausgeführt, um der Seite Quizpools und -Tasks
    # für die Darstellung zu übergeben

    return render(request, 'singleplayer/sp_new_game.html',
                  get_library_content())


def show_lib_content(request, pool_id=None, game_id=None):
    # Rückgabe:
    selected_pool = None
    if bool(pool_id):
        selected_pool = QuizPool.objects.get(id=pool_id)

    return render(request, 'singleplayer/sp_new_game_content.html',
                  get_library_content(selected_pool=selected_pool))


# Game
def create_game(request, pool_id):
    quizpool = QuizPool.objects.get(id=pool_id)
    timestamp = dt.datetime.now()
    # Game Objekt erstellen
    sp_game = SPGame(name=quizpool.name + ' - ' + timestamp.strftime('%d.%m.%Y %H:%M'),
                     user=request.user,
                     pool=quizpool, )
    sp_game.save()

    # SPGame_contains_Quiztask Objekt erstellen und damit Quiztasks dem Game zuordnen
    quiztasks = QuizTask.objects.filter(pool=quizpool)

    for task in quiztasks:
        sp_game_quiztasks = SPGame_contains_Quiztask(
            game=sp_game,
            task=task, )
        sp_game_quiztasks.save()

    redirect_url = '/singleplayer/sp_game/' + str(sp_game.id)
    return redirect(redirect_url)

def render_game(request, game_id: int):
    # pool_id: int, sp_game: SPGame, questions_status_list: list, quiztask_answers: dict):
    sp_game = SPGame.objects.get(id=game_id)
    pool_id = sp_game.pool_id
    quiztasks = QuizTask.objects.filter(pool=pool_id)

    questions_list = get_questions_by_game(sp_game)
    first_quiztask = quiztasks[0]  # Erste quiztask für die Anzeige der ersten quiztask-card
    quiztask_answers = get_quiztask_answers(first_quiztask.id)

    return render(request, 'singleplayer/sp_game.html',
                  {'sp_game': sp_game,
                   'questions_list': questions_list,
                   'quiztask_answers': quiztask_answers,
                   })


def render_quiztask_card(request, game_id, task_id, action, selected_answer_id=None):
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

    return render(request, 'singleplayer/quiztask_card.html',
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
        sp_game_quiztask = SPGame_contains_Quiztask.objects.get(game_id=game_id, task_id=task_id)
        sp_game_quiztask.selected_answer = Answer.objects.get(id=selected_answer_id)
        sp_game_quiztask.correct_answered = True
        sp_game_quiztask.completed = True
        sp_game_quiztask.save()

        result = get_evaluation_result(True)

    else:
        sp_game_quiztask = SPGame_contains_Quiztask.objects.get(game_id=game_id, task_id=task_id)
        sp_game_quiztask.selected_answer = Answer.objects.get(id=selected_answer_id)
        sp_game_quiztask.correct_answered = False
        sp_game_quiztask.completed = True
        sp_game_quiztask.save()

        result = get_evaluation_result(False)

    quiztask_answers = get_quiztask_answers(task_id)

    # Prüfen, ob alle Aufgaben beantwortet wurden
    game_completed = check_game_completed(game=current_game)
    if game_completed:
        current_game.completed_at = dt.datetime.now()
        current_game.completed = True
        current_game.save()

    return render(request, 'singleplayer/quiztask_card.html',
                  {'sp_game': current_game,
                   'quiztask_answers': quiztask_answers,
                   'selected_answer_id': selected_answer_id,
                   'result': result
                   })


def render_game_result_card(request, game_id):
    sp_game = SPGame.objects.get(id=game_id)

    # Ermitteln und speichern Gesamtergebnis des Spiels
    correct_percent = get_game_stats(sp_game)
    sp_game.correct_percent = correct_percent
    sp_game.save()

    # returns
    questions_list = get_questions_by_game(sp_game)
    pool_stats = get_pool_stats(sp_game)
    avg_correct_percent = pool_stats['avg_correct_percent']
    games_count = pool_stats['games_count']
    quiztask_stats = pool_stats['quiztask_stats']

    return render(request, 'singleplayer/game_result_card.html',
                  {'sp_game': sp_game,
                   'questions_list': questions_list,
                   'avg_correct_percent': avg_correct_percent,
                   'games_count': games_count,
                   'quiztask_stats': quiztask_stats,
                   })

# Fortsetzen
def sp_resume_game(request):
    # Rückgabe:
    unfinished_games = get_unfinished_games(request.user.id)

    return render(request, 'singleplayer/sp_resume_game.html',
                  {'unfinished_games': unfinished_games})

def show_game_content(request, game_id=None):
    # Zeigt vorhandene bzw abgeschlossene Spiele

    # Rückgabe:

    selected_game = None
    selected_pool = None
    if bool(game_id):
        selected_game = SPGame.objects.get(id=game_id)
        selected_pool = QuizPool.objects.get(id=selected_game.pool_id)

    quiztasks = get_library_content(selected_pool=selected_pool)['quiztasks']

    if 'singleplayer/sp_resume_game' in request.headers['Hx-Current-Url']:
        unfinished_games = get_unfinished_games(request.user.id)
        return render(request, 'singleplayer/sp_resume_game_content.html',
                      {'unfinished_games': unfinished_games,
                       'quiztasks': quiztasks,
                       'selected_game': selected_game})
    elif 'singleplayer/sp_history' in request.headers['Hx-Current-Url']:
        finished_games = get_finished_games(request.user.id)
        # questions_status_list = get_questions_by_game(selected_game)
        pool_stats = get_pool_stats(selected_game)
        return render(request, 'singleplayer/sp_history_content.html',
                      {'finished_games': finished_games,
                       # 'quiztasks': quiztasks,
                       'sp_game': selected_game,
                       'avg_correct_percent': pool_stats['avg_correct_percent'],
                       'games_count': pool_stats['games_count'],
                       'quiztask_stats': pool_stats['quiztask_stats'],
                       })


# History
def sp_history(request):
    # Rückgabe:
    finished_games = get_finished_games(request.user.id)

    return render(request, 'singleplayer/sp_history.html',
                  {'finished_games': finished_games})