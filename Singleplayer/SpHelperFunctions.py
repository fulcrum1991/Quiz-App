# Hilfsfunktionen zu Singleplayer/views.py
from Library.models import QuizTask, Answer
from Singleplayer.models import SPGame_contains_Quiztask, SPGame

def get_questions_by_game(sp_game):
    # Erstellt eine Liste von Dictionaries. Jedes Element (Dictionary) enhählt Informationen zu einer Quiztask, bestehend aus
    # task.id, der question und dem Status, ob diese Quiztask bereits richtig beantwortet wurde.
    # Rückgabe: Diese Liste
    questions_list = []

    gametasks_by_game = SPGame_contains_Quiztask.objects.filter(game=sp_game)

    for gametask in gametasks_by_game:
        questions_list.append({'task_id': gametask.id,
                                      'question': QuizTask.objects.get(id=gametask.task_id).question,
                                      })
    return questions_list

def get_quiztask_answers(task_id):
    # Erfragt Quiztask-Objekt und die dazugehörigen Answer-Objekte.
    # Rückgabe: Dictionary bestehend aus einem Quiztask-Objekt und den dazugehörigen Answer-Objekten
    quiztask = QuizTask.objects.get(id=task_id)
    answers = Answer.objects.filter(task_id=task_id)

    return {'quiztask': quiztask, 'answers': answers}

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

def get_game_stats(game: SPGame):
    quiztasks = SPGame_contains_Quiztask.objects.filter(game=game)
    count_correct_answered = 0
    number_of_quiztasks = quiztasks.__len__()

    for task in quiztasks:
        if task.correct_answered:
            count_correct_answered += 1

    correct_percent = count_correct_answered / number_of_quiztasks * 100
    return correct_percent

def get_pool_stats(game: SPGame):
    # Queryset: Spiele aus dem gleichen Quizpool vom gleichen Nutzer
    games_with_pool = SPGame.objects.filter(pool_id=game.pool_id, user_id=game.user_id, completed=True)
    games_count = games_with_pool.__len__()

    # Zählung richtiger/falscher Antworten pro Frage
    # {'id': {'correct': 0, 'wrong': 0}}
    quiztask_stats = {}
    for game in games_with_pool:
        gametasks = SPGame_contains_Quiztask.objects.filter(game=game)

        for gametask in gametasks:
            if gametask.task_id not in quiztask_stats.keys():
                quiztask_stats[gametask.task_id] = {
                    'question': QuizTask.objects.get(id=gametask.task_id).question,
                    'correct_answered': gametask.correct_answered,
                    'correct': 0,
                    'wrong': 0}
            if gametask.correct_answered:
                quiztask_stats[gametask.task_id]['correct'] += 1
            elif gametask.correct_answered == False:
                quiztask_stats[gametask.task_id]['wrong'] += 1

    # Prozentrechnung zu durchschnittlich richtigen Antworten
    correct_percent_list = []
    for game in games_with_pool:
        correct_percent_list.append(game.correct_percent)
    avg_correct_percent = sum(correct_percent_list) / len(correct_percent_list)

    return {'avg_correct_percent': avg_correct_percent,
            'games_count': games_count,
            'quiztask_stats': quiztask_stats}

def get_unfinished_games(user_id: int):
    unfinished_games = SPGame.objects.filter(user_id=user_id, completed=False)

    return unfinished_games

def get_finished_games(user_id: int):
    finished_games = SPGame.objects.filter(user_id=user_id, completed=True)

    return finished_games