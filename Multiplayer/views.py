# views.py

import datetime as dt

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from Library.models import QuizPool, Answer, QuizTask
from Singleplayer.SpHelperFunctions import get_quiztask_answers
from .MPHelperFunctions import get_next_turn, get_mp_game_stats, check_mp_game_completed
from .models import MPGame, MPGame_contains_Quiztask


@login_required(login_url='/login')
def mp_overview(request):
    return render(request, 'multiplayer/mp_overview.html')


@login_required(login_url='/login')
def mp_new_game(request):
    pools = QuizPool.objects.all()
    return render(request, 'multiplayer/mp_new_game.html', {'pools': pools})


@login_required(login_url='/login')
def join_game(request, pool_id):
    pool = get_object_or_404(QuizPool, id=pool_id)

    # Suche nach einem bestehenden Spiel, das noch nicht voll ist
    existing_game = MPGame.objects.filter(pool=pool, player2__isnull=True).first()

    if existing_game:
        # Wenn ein bestehendes Spiel gefunden wird
        if existing_game.is_full():
            # Weiterleitung zur Lobby, falls das Spiel voll ist
            return redirect('multiplayer:mp_lobby', game_id=existing_game.id)
        else:
            # Spieler kann dem Spiel beitreten, das noch nicht voll ist
            if request.user != existing_game.player1:
                existing_game.player2 = request.user  # Füge den zweiten Spieler hinzu
                existing_game.save()
            return redirect('multiplayer:mp_lobby', game_id=existing_game.id)
    else:
        # Erstelle ein neues Spiel, falls kein bestehendes Spiel gefunden wird
        new_game = MPGame.objects.create(pool=pool, player1=request.user)
        return redirect('multiplayer:mp_lobby', game_id=new_game.id)


@login_required(login_url='/login')
def mp_lobby(request, game_id):
    game = get_object_or_404(MPGame, id=game_id)

    # Wenn das Spiel vollständig ist (zwei Spieler vorhanden)
    if game.is_full():
        # Überprüfen, ob bereits Aufgaben zugewiesen wurden
        if not MPGame_contains_Quiztask.objects.filter(game=game).exists():
            # Falls nicht, weise Aufgaben zu
            assign_tasks_to_game(game)

        # Weiterleitung zum eigentlichen Spiel
        return redirect('multiplayer:render_game', game_id=game.id)

    # Falls das Spiel noch nicht voll ist, zeige die Lobby an
    return render(request, 'multiplayer/mp_lobby.html', {'game': game})


@login_required(login_url='/login')
def render_game(request, game_id):
    game = get_object_or_404(MPGame, id=game_id)

    # Hole alle Aufgaben des Spiels
    tasks = MPGame_contains_Quiztask.objects.filter(game=game)

    # Hole die erste nicht abgeschlossene Aufgabe
    current_task = tasks.filter(completed=False).first()

    if current_task is None:
        # Wenn es keine offenen Aufgaben mehr gibt, markiere das Spiel als abgeschlossen
        game.completed = True
        game.save()
        # Weiterleitung zur Spiel-Resultat-Seite
        return redirect('multiplayer:mp_game_result', game_id=game.id)

    # Hole die Antworten für die aktuelle Quizaufgabe
    quiztask_answers = get_quiztask_answers(current_task.task.id)

    return render(request, 'multiplayer/mp_game.html', {
        'game': game,
        'tasks': tasks,
        'quiztask_answers': quiztask_answers,
        'current_task': current_task,
    })


def render_quiztask_card(request, game_id, task_id, action):
    game = MPGame.objects.get(id=game_id)
    task = MPGame_contains_Quiztask.objects.get(id=task_id, game=game)

    if action == 'select_answer':
        # Nur der Spieler, der an der Reihe ist, darf antworten
        if task.current_turn == request.user:
            selected_answer_id = request.POST.get('selected_answer')

            if selected_answer_id:
                try:
                    answer = Answer.objects.get(id=selected_answer_id)
                    if request.user == game.player1:
                        task.player1_answer = answer
                    else:
                        task.player2_answer = answer

                    # Wechsle den Zug zum nächsten Spieler
                    task.current_turn = get_next_turn(task.current_turn, game.player1, game.player2)
                    task.save()
                except Answer.DoesNotExist:
                    return HttpResponseBadRequest("Selected answer does not exist.")
            else:
                return HttpResponseBadRequest("No answer selected.")

        # Überprüfen, ob beide Spieler geantwortet haben
        if task.player1_answer and task.player2_answer:
            task.completed = True
            task.save()

    # Lade die Antworten für die aktuelle Quizaufgabe
    quiztask_answers = get_quiztask_answers(task.task.id)

    # Falls die Seite erneut gerendert wird, gib eine HttpResponse zurück
    return render(request, 'multiplayer/quiztask_card.html', {
        'game': game,
        'task': task,
        'quiztask_answers': quiztask_answers,
    })




@login_required(login_url='/login')
def evaluate_task(request, game_id, task_id):
    game = get_object_or_404(MPGame, id=game_id)
    task = get_object_or_404(MPGame_contains_Quiztask, id=task_id, game=game)

    # Hole die ausgewählte Antwort
    selected_answer_id = request.POST.get('answer')
    selected_answer = get_object_or_404(Answer, id=selected_answer_id)

    if request.user == game.player1:
        task.player1_answer = selected_answer
    elif request.user == game.player2:
        task.player2_answer = selected_answer

    task.save()

    # Wenn beide Spieler die Aufgabe abgeschlossen haben, markiere sie als abgeschlossen
    if task.player1_answer and task.player2_answer:
        task.completed = True
        task.save()

    # Dynamische Rückmeldung nach der Auswahl
    return render(request, 'multiplayer/partials/answer_feedback.html', {
        'selected_answer': selected_answer,
    })


@login_required(login_url='/login')
def mp_game_result(request, game_id):
    game = get_object_or_404(MPGame, id=game_id)

    # Berechnung der Ergebnisse basierend auf den gespeicherten Antworten
    stats = get_mp_game_stats(game)
    player1_percent = stats['player1_percent']
    player2_percent = stats['player2_percent']

    return render(request, 'multiplayer/mp_game_result.html', {
        'game': game,
        'player1_percent': player1_percent,
        'player2_percent': player2_percent,
        'stats': stats  # Stelle sicher, dass das aktualisierte 'stats' Dictionary übergeben wird
    })


@login_required(login_url='/login')
def mp_resume_game(request):
    # Finde alle unvollendeten Spiele des aktuellen Benutzers
    unfinished_games = MPGame.objects.filter(
        completed=False
    ).filter(
        player1=request.user
    ) | MPGame.objects.filter(
        completed=False, player2=request.user
    )

    return render(request, 'multiplayer/mp_resume_game.html', {
        'unfinished_games': unfinished_games
    })



@login_required(login_url='/login')
def show_game_content(request, game_id=None):
    selected_game = None
    selected_pool = None

    if game_id:
        selected_game = MPGame.objects.get(id=game_id)
        selected_pool = QuizPool.objects.get(id=selected_game.pool_id)

    quiztasks = MPGame_contains_Quiztask.objects.filter(game=selected_game)

    if 'multiplayer/mp_resume_game' in request.headers['Hx-Current-Url']:
        unfinished_games = MPGame.objects.filter(completed=False, player1=request.user) | MPGame.objects.filter(
            completed=False, player2=request.user)
        return render(request, 'multiplayer/mp_resume_game_content.html', {
            'unfinished_games': unfinished_games,
            'quiztasks': quiztasks,
            'selected_game': selected_game,
        })
    elif 'multiplayer/mp_history' in request.headers['Hx-Current-Url']:
        finished_games = MPGame.objects.filter(completed=True, player1=request.user) | MPGame.objects.filter(
            completed=True, player2=request.user)
        return render(request, 'multiplayer/mp_history_content.html', {
            'finished_games': finished_games,
            'selected_game': selected_game,
            'quiztasks': quiztasks,
        })


@login_required(login_url='/login')
def mp_history(request):
    finished_games = MPGame.objects.filter(completed=True, player1=request.user) | MPGame.objects.filter(completed=True,
                                                                                                         player2=request.user)
    return render(request, 'multiplayer/mp_history.html', {'finished_games': finished_games})

def assign_tasks_to_game(game):
    tasks = QuizTask.objects.filter(pool=game.pool)[:5]  # Begrenze die Anzahl auf 5 Aufgaben
    for task in tasks:
        # Setze current_turn explizit auf den ersten Spieler
        MPGame_contains_Quiztask.objects.create(game=game, task=task, current_turn=game.player1)
    print(f"{len(tasks)} Aufgaben wurden dem Spiel {game.id} zugewiesen.")

@login_required(login_url='/login')
def mp_lobby_content(request, game_id):
    game = get_object_or_404(MPGame, id=game_id)

    # Wenn das Spiel vollständig ist, sende einen Redirect-Header für HTMX
    if game.is_full():
        response = JsonResponse({'location': reverse('multiplayer:render_game', args=[game.id])})
        response['HX-Redirect'] = reverse('multiplayer:render_game', args=[game.id])
        return response

    return render(request, 'multiplayer/mp_lobby_content.html', {'game': game})

@login_required(login_url='/login')
def quiztask_status(request, game_id):
    game = get_object_or_404(MPGame, id=game_id)

    # Hole die aktuelle, nicht abgeschlossene Aufgabe
    current_task = MPGame_contains_Quiztask.objects.filter(game=game, completed=False).first()

    if current_task is None:
        # Wenn alle Aufgaben abgeschlossen sind, leite zur Ergebnisseite weiter
        return redirect('multiplayer:mp_game_result', game_id=game.id)

    quiztask_answers = get_quiztask_answers(current_task.task.id)

    # Render the updated task and answers
    return render(request, 'multiplayer/partials/answer_form.html', {
        'game': game,
        'task': current_task,
        'quiztask_answers': quiztask_answers,
    })


@login_required(login_url='/login')
def check_game_status(request, game_id):
    game = get_object_or_404(MPGame, id=game_id)

    if game.is_full():
        # JSON-Antwort mit der Redirect-URL, sobald das Spiel voll ist
        return JsonResponse({'redirect_url': reverse('multiplayer:render_game', args=[game.id])})

    return JsonResponse({'status': 'waiting'})




















