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
#
# Singleplayer menu
#
@login_required(login_url='/login')
def sp_overview(request):
    """
    Handles the requests for the single-player game overview page.

    :param request: The HTTP request received.

    :return: The HttpResponse to be sent to the client.
    """
    return render(request, 'singleplayer/sp_overview.html')


def sp_new_game(request):
    """
    The `sp_new_game` view function handles the requests to start a new single-player game.

    :param request: The HTTP request received.
    :return: The rendered 'singleplayer/sp_new_game.html' template.

    Additional context is provided to the template using the `get_library_content()` function.
    This function is likely to fetch the quizpools and tasks for display on the page.
    """

    return render(request, 'singleplayer/sp_new_game.html',
                  get_library_content())


def show_lib_content(request, pool_id=None, game_id=None):
    """
    The `show_lib_content` view function handles the requests to display the content of the library in single-player game.

    :param request: The HTTP request received.
    :param pool_id: (Optional) ID of the specific QuizPool to be selected and displayed.
    :param game_id: (Optional) ID of the specific game, not used in the current context but might be part of the larger view logic.
    :return: The rendered 'singleplayer/sp_new_game_content.html' template.
    """
    selected_pool = None
    if bool(pool_id):
        selected_pool = QuizPool.objects.get(id=pool_id)

    return render(request, 'singleplayer/sp_new_game_content.html',
                  get_library_content(selected_pool=selected_pool))

#
# Game
#
def create_game(request, pool_id):
    """
    The `create_game` view function handles the creation of a new game in the single-player mode.

    :param request: The HTTP request received.
    :param pool_id: The ID of the QuizPool selected for the game.

    :return: Redirect to the newly created game.

    An `SPGame` object is created with the name derived from the QuizPool's name and the current timestamp.
    Associated `QuizTask` objects for the selected QuizPool are fetched and associated with the game
    via `SPGame_contains_Quiztask` relation. After the successful creation of the game, a redirection is performed to
    the game's page.
    """
    # Fetch the QuizPool object with the provided pool_id and current timestamp
    quizpool = QuizPool.objects.get(id=pool_id)
    timestamp = dt.datetime.now()

    # Create a new SPGame object with name composed of QuizPool's name and the current timestamp
    # Associate the current user and the selected QuizPool with the game
    sp_game = SPGame(name=quizpool.name + ' - ' + timestamp.strftime('%d.%m.%Y %H:%M'),
                     user=request.user,
                     pool=quizpool, )
    sp_game.save()

    # Fetch the QuizTask objects associated with the selected QuizPool and for each QuizTask, create a
    # SPGame_contains_Quiztask association, linking the QuizTask with the SPGame
    quiztasks = QuizTask.objects.filter(pool=quizpool)
    for task in quiztasks:
        sp_game_quiztasks = SPGame_contains_Quiztask(
            game=sp_game,
            task=task, )
        sp_game_quiztasks.save()

    # After the successful creation of the game, redirect to the newly created game's page
    redirect_url = '/singleplayer/sp_game/' + str(sp_game.id)
    return redirect(redirect_url)

def render_game(request, game_id: int):
    """
    The `render_game` function handles the task of rendering a single player game.

    :param request: An HTTP request instance
    :param game_id: An integer representing the ID of the game to be rendered
    :return: A render of the single player game HTML template

    The function retrieves the `SPGame` instance corresponding to the provided game_id and other associated objects.
    It also fetches the list of questions for the game and the answers for the first question. These are then fed into
    the 'singleplayer/sp_game.html' template.
    """
    # Fetch the SPGame object corresponding to the provided game_id; Extract the pool_id from the fetched
    # SPGame object and fetch the first QuizTask object associated with the identified QuizPool
    sp_game = SPGame.objects.get(id=game_id)
    pool_id = sp_game.pool_id
    first_quiztask = QuizTask.objects.filter(pool=pool_id).first()

    # Retrieve the list of questions pertaining to the game and fetch the answers linked to the first quiz task
    questions_list = get_questions_by_game(sp_game)
    quiztask_answers = get_quiztask_answers(first_quiztask.id)

    # Render the 'singleplayer/sp_game.html' template with the established context and return the HTTP response
    return render(request, 'singleplayer/sp_game.html',
                  {'sp_game': sp_game,
                   'questions_list': questions_list,
                   'quiztask_answers': quiztask_answers,
                   })


def render_quiztask_card(request, game_id, task_id, action, selected_answer_id=None):
    """
    The `render_quiztask_card` function handles the rendering of a single question card
    in a single player game.

    :param request: An HTTP request instance.
    :param game_id: An integer representing the ID of the game.
    :param task_id: An integer representing the ID of the current quiz task.
    :param action: A string that represents the action to be performed, such as 'next' for next question,
                   'previous' for the previous question, or 'select_answer' for selecting an answer.
    :param selected_answer_id: Optional, an integer representing the ID of the selected answer.
    :return: A render of the quiz task card HTML template.

    The function first retrieves the `SPGame` and `QuizTask` instances associated with the respective
    game_id and task_id. Based on the action, it either fetches the next or previous question or does nothing.
    Then it fetches the answers for the current quiz task. If the task was completed, it fetches the result of the evaluation
    of that task and the ID of the selected answer. Finally, this information is fed into the 'singleplayer/quiztask_card.html' template.
    """

    # Retrieve the current game instance and the quiztasks associated with the current game
    current_game = SPGame.objects.get(id=game_id)
    quiztasks = SPGame_contains_Quiztask.objects.filter(game=current_game)

    # Respond to navigation button 'Next' and 'Previous'
    if action == 'next':
        task_id = get_next_task(task_id, quiztasks)
    elif action == 'previous':
        task_id = get_previous_task(task_id, quiztasks)
    elif action == 'select_answer':
        pass

    # Retrieve the current task and fetch answers for the current quiztask
    current_task = quiztasks.get(task_id=task_id)
    quiztask_answers = get_quiztask_answers(task_id)

    # If the current task was completed, get the evaluation result and the selected answer ID
    result = None
    if current_task.completed == True:
        result = get_evaluation_result(current_task.correct_answered)
        selected_answer_id = current_task.selected_answer_id

    # Render the 'singleplayer/quiztask_card.html' template with the context and return the HTTP response
    return render(request, 'singleplayer/quiztask_card.html',
                  {'sp_game': current_game,
                   'quiztask_answers': quiztask_answers,
                   'selected_answer_id': selected_answer_id,
                   'result': result
                   })


def evaluate_task(request, game_id: int, task_id: int, selected_answer_id: int):
    """
    The `evaluate_task` function handles the evaluation of a single task in a single-player game and
    updates the game progress.

    :param request: An HTTP request instance.
    :param game_id: An integer representing the ID of a game.
    :param task_id: An integer representing the ID of a task.
    :param selected_answer_id: An integer, the ID of the selected answer.
    :return: Render of the quiz task card HTML template.

    This function fetches the SPGame and Answer instances with the specified game_id and selected_answer_id,
    respectively. It then checks whether the selected answer is correct. If it is correct, it fetches the
    corresponding SPGame_contains_Quiztask instance and updates its fields as completed and correctly answered,
    and saves the changes. The get_evaluation_result function is called with True as the argument to get the
    result of the task.

    If the selected answer is not correct, it fetches the corresponding SPGame_contains_Quiztask
    instance and updates it as completed but not correctly answered, and saves these changes.
    The get_evaluation_result function is called with False as the argument to get the result of the task.

    After evaluating, it checks whether all tasks in the game have been completed.
    If all tasks are completed, it updates the current_game instance as completed and saves the current time as the
    completion time.

    This function finally returns a render of the quiz_task card HTML template with necessary data.
    """
    # Fetch current game and selected answer instances
    current_game = SPGame.objects.get(id=game_id)
    selected_answer = Answer.objects.get(id=selected_answer_id)

    result = None

    # If the selected answer is correct,
    if selected_answer.correct == True:
        sp_game_quiztask = SPGame_contains_Quiztask.objects.get(game_id=game_id, task_id=task_id)
        sp_game_quiztask.selected_answer = Answer.objects.get(id=selected_answer_id)
        sp_game_quiztask.correct_answered = True
        sp_game_quiztask.completed = True
        sp_game_quiztask.save()

        # Get the result of the evaluation
        result = get_evaluation_result(True)

    # If the selected answer is wrong,
    else:
        sp_game_quiztask = SPGame_contains_Quiztask.objects.get(game_id=game_id, task_id=task_id)
        sp_game_quiztask.selected_answer = Answer.objects.get(id=selected_answer_id)
        sp_game_quiztask.correct_answered = False
        sp_game_quiztask.completed = True
        sp_game_quiztask.save()

        # Get the result of the evaluation
        result = get_evaluation_result(False)

    quiztask_answers = get_quiztask_answers(task_id)

    # Check if all the tasks have been answered
    game_completed = check_game_completed(game=current_game)
    if game_completed:
        current_game.completed_at = dt.datetime.now()
        current_game.completed = True
        current_game.save()

    # Render the HTML template with the provided context
    return render(request, 'singleplayer/quiztask_card.html',
                  {'sp_game': current_game,
                   'quiztask_answers': quiztask_answers,
                   'selected_answer_id': selected_answer_id,
                   'result': result
                   })


def render_game_result_card(request, game_id: int):
    """
    The `render_game_result_card` function handles the rendering of the game result card
    for a given single-player game identified by the parameter game_id.

    :param request: An HTTP request instance.
    :param game_id: An integer, the ID of the single-player game.
    :return: A render of the game result card HTML template.

    This function fetches the SPGame instance with the provided game_id.
    It then uses the get_game_stats function to find out the percentage of correct answers in the game,
    saves it into the fetched SPGame instance and commits the change to the database.

    It retrieves the list of questions for the game using get_questions_by_game function
    and calls get_pool_stats function to get statistical data of the game,
    like the average correctness percentage among all the games,
    the total numbers of games played, and statistics for quiz tasks.

    The identified SPGame instance, the list of questions, and the statistical data are then used
    to render the 'singleplayer/game_result_card.html' template.
    """
    # Fetch the SPGame instance with game_id and compute the overall game result
    sp_game = SPGame.objects.get(id=game_id)

    # Save the computed result into SPGame object
    correct_percent = get_game_stats(sp_game)
    sp_game.correct_percent = correct_percent
    sp_game.save()

    # Get a list of questions in the game and gather statistics about the game
    questions_list = get_questions_by_game(sp_game)
    pool_stats = get_pool_stats(sp_game)
    avg_correct_percent = pool_stats['avg_correct_percent']
    games_count = pool_stats['games_count']
    quiztask_stats = pool_stats['quiztask_stats']

    # Define the context to be passed into the rendering engine
    return render(request, 'singleplayer/game_result_card.html',
                  {'sp_game': sp_game,
                   'questions_list': questions_list,
                   'avg_correct_percent': avg_correct_percent,
                   'games_count': games_count,
                   'quiztask_stats': quiztask_stats,
                   })
#
# Spiel Fortsetzen
#
def sp_resume_game(request):
    """
    The `sp_resume_game` function enables the users to resume unfinished single-player games.

    :param request: An HTTP request instance.
    :return: Render of Single-player Resume Game HTML template.

    The function fetches all unfinished games of the current user using the `get_unfinished_games` function
    with user's id as a parameter and then renders the 'singleplayer/sp_resume_game.html' template with
    the list of the user's unfinished games.

    """
    # Fetch user's unfinished games by user's id from the session request provide them to be
    # rendered in the HTML template
    unfinished_games = get_unfinished_games(request.user.id)
    return render(request, 'singleplayer/sp_resume_game.html',
                  {'unfinished_games': unfinished_games})

def show_game_content(request, game_id=None):
    """
   The `show_game_content` function handles the display of existing or completed games depending
   on the current requested page.

   :param request: An HTTP request instance.
   :param game_id: An integer or None. Default value is None. Represents the id of the game.
   :return: Render of Single Player Resume Game / Single Player History HTML template.

   Based on the `game_id` provided, the function fetches the SPGame and QuizPool objects and then gets the quiz tasks
   in the library using the `get_library_content` function. According to the header of the request, the function
   prepares data for the template of either the resumed games page or game history page.

   For 'singleplayer/sp_resume_game', it fetches the unfinished games of the user using the `get_unfinished_games` function
   with user's id, and renders 'singleplayer/sp_resume_game_content.html' with the list of unfinished games, quiz tasks,
    and the selected game.

   For 'singleplayer/sp_history', it fetches the completed games of the user using the `get_finished_games` function
   with user's id and gets game statistics with `get_pool_stats` function. It then renders 'singleplayer/sp_history_content.html'
   with the list of finished games, selected game, and games statistics.
   """

    selected_game = None
    selected_pool = None

    # If game_id is provided, make queries to retrieve related info
    if bool(game_id):
        selected_game = SPGame.objects.get(id=game_id)
        selected_pool = QuizPool.objects.get(id=selected_game.pool_id)

    # Get quiz tasks related to selected game's pool
    quiztasks = get_library_content(selected_pool=selected_pool)['quiztasks']

    # Check request's header to decide next action
    if 'singleplayer/sp_resume_game' in request.headers['Hx-Current-Url']:
        unfinished_games = get_unfinished_games(request.user.id)
        # If in resume game page, return related game contents
        return render(request, 'singleplayer/sp_resume_game_content.html',
                      {'unfinished_games': unfinished_games,
                       'quiztasks': quiztasks,
                       'selected_game': selected_game})
    elif 'singleplayer/sp_history' in request.headers['Hx-Current-Url']:
        finished_games = get_finished_games(request.user.id)
        pool_stats = get_pool_stats(selected_game)
        # If in game history page, return related game contents
        return render(request, 'singleplayer/sp_history_content.html',
                      {'finished_games': finished_games,
                       # 'quiztasks': quiztasks,
                       'sp_game': selected_game,
                       'avg_correct_percent': pool_stats['avg_correct_percent'],
                       'games_count': pool_stats['games_count'],
                       'quiztask_stats': pool_stats['quiztask_stats'],
                       })

#
# History
#
def sp_history(request):
    """
    The `sp_history` function allows users to view their game history.

    :param request: An HTTP request instance.
    :return: Render of Single Player History Page HTML template.

    The function fetches all the completed games of the current user using
    `get_finished_games` function with user's id as a parameter and then renders
    the 'singleplayer/sp_history.html' template with the list of user's completed games.
    """

    # Fetch all completed games of the current user and uns them to render the HTML template
    finished_games = get_finished_games(request.user.id)
    return render(request, 'singleplayer/sp_history.html',
                  {'finished_games': finished_games})