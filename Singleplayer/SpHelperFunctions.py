# Hilfsfunktionen zu Singleplayer/views.py
from Library.models import QuizTask, Answer
from Singleplayer.models import SPGame_contains_Quiztask, SPGame

def get_questions_by_game(sp_game):
    """
        Generates a list of dictionaries, where each dictionary contains information about a Quiztask.
        Each dictionary consist of `task.id`, the `question` and the status whether the Quiztask was answered correctly.

        :param sp_game: The game instance to get its related Quiztasks.

        :return: A list of dictionaries where each dictionary has information about a Quiztask.
    """

    # For each game task, get the corresponding QuizTask, store id and question in a dictionary,
    # and add the dictionary to the list
    questions_list = []
    gametasks_by_game = SPGame_contains_Quiztask.objects.filter(game=sp_game)
    for gametask in gametasks_by_game:
        questions_list.append({'task_id': gametask.id,
                               'question': QuizTask.objects.get(id=gametask.task_id).question,
        })
    # Return the list of dictionaries
    return questions_list

def get_quiztask_answers(task_id: int):
    """
    Query the QuizTask object and its related Answer objects.

    :param task_id: ID of the QuizTask for which associated Answer objects are to be fetched.

    :return: A dictionary comprising a QuizTask object and its related Answer objects.
    """
    quiztask = QuizTask.objects.get(id=task_id)
    answers = Answer.objects.filter(task_id=task_id)

    return {'quiztask': quiztask, 'answers': answers}

def get_next_task(task_id: int, quiztasks: SPGame_contains_Quiztask):
    """
    Returns the id of the next task in the provided `quiztasks`.

    :param task_id: The id of the current task.
    :param quiztasks: A set of Quiz tasks to search the next task from.

    :return: The id of the next task. If no next task is found, returns None.
    """

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
    """
    Returns the id of the previous task in the provided `quiztasks`.

    :param task_id: The id of the current task.
    :param quiztasks: A set of Quiz tasks to search the previous task from.

    :return: The id of the previous task. If no previous task is found, returns None.
    """

    new_task_id = quiztasks.first().id
    for task in quiztasks:
        if task.task_id != task_id:
            new_task_id = task.task_id
        else:
            break

    return new_task_id

def get_evaluation_result(correct_answered: bool):
    """
    Returns a dictionary containing evaluation result and corresponding response message.

    :param correct_answered: A boolean indicating whether the answer was correct.

    :return: A dictionary with keys 'correct_answered' and 'answer_message'.
    """
    result = {'correct_answered': correct_answered, 'answer_message': ''}

    if correct_answered:
        result['answer_message'] = 'Die Antwort ist richtig.'
    else:
        result['answer_message'] = 'Die Antwort ist falsch.'

    return result

def check_game_completed(game: SPGame):
    """
    Checks whether all tasks in a game are completed.

    :param game: The SPGame object which status is to be checked.

    :return: True if the game is completed, i.e., all the tasks in the game are completed. Otherwise, return False.
    """

    unfinished_tasks = SPGame_contains_Quiztask.objects.filter(game=game, completed=False)
    if unfinished_tasks.__len__() == 0:
        return True
    else:
        return False

def get_game_stats(game: SPGame):
    """
    Returns the percentage of correctly answered tasks in a game.

    :param game: The SPGame object which stats are to be pulled.

    :return: The percentage of correctly answered tasks in the game.
    """

    # Get all tasks related to the provided game. Initialize a counter to keep track of correctly
    # answered tasks, Get the total number of tasks
    quiztasks = SPGame_contains_Quiztask.objects.filter(game=game)
    count_correct_answered = 0
    number_of_quiztasks = quiztasks.__len__()

    # Iterate over all tasks, and increment the count for each task that was correctly answered
    for task in quiztasks:
        if task.correct_answered:
            count_correct_answered += 1

    # Calculate the percentage and return result
    correct_percent = count_correct_answered / number_of_quiztasks * 100
    return correct_percent

def get_pool_stats(game: SPGame):
    """
    Generates statistics for all games from the same quiz pool as provided game for the same user.

    :param game: The SPGame object for which pool's statistics are to be computed.

    :return: A dictionary containing the average percentage of correct answers, count of games and statistics for
    each quiz task.
    """

    # Queryset: Games from the same quiz pool from the same user
    games_with_pool = SPGame.objects.filter(pool_id=game.pool_id, user_id=game.user_id, completed=True)
    print(games_with_pool)
    # Count of games in the quiz pool
    games_count = games_with_pool.__len__()

    # Count of correct/wrong answers per question
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
            # Increase the count of correct answers if the answer is correct
            if gametask.correct_answered:
                quiztask_stats[gametask.task_id]['correct'] += 1
            # Increase the count of wrong answers if the answer is incorrect
            elif gametask.correct_answered == False:
                quiztask_stats[gametask.task_id]['wrong'] += 1

    # Computing average of correct answers percentage
    correct_percent_list = []
    for game in games_with_pool:
        correct_percent_list.append(game.correct_percent)
    avg_correct_percent = sum(correct_percent_list) / len(correct_percent_list)

    # Returning the compiled stats
    return {'avg_correct_percent': avg_correct_percent,
            'games_count': games_count,
            'quiztask_stats': quiztask_stats}

def get_unfinished_games(user_id: int):
    """
    Fetches all incomplete single player games tied to a given user.

    :param user_id: Integer id of the user.

    :return: QuerySet containing the unfinished games of the user.
    """
    unfinished_games = SPGame.objects.filter(user_id=user_id, completed=False)

    return unfinished_games

def get_finished_games(user_id: int):
    """
    Fetches all complete single player games tied to a given user.

    :param user_id: Integer id of the user.

    :return: QuerySet containing the finished games of the user.
    """
    finished_games = SPGame.objects.filter(user_id=user_id, completed=True)

    return finished_games