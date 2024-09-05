from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods

from .forms import QuizPoolForm, QuizTaskForm, AnswerForm
from .models import QuizPool, QuizTask, Answer



# Create your views here.
#
# Library
#
def get_library_content(selected_pool=None, selected_task = None):
    """
    This method retrieves quizpool and quiztask objects from the database and returns them in a dictionary.
    It can be used by other functions for rendering the library. If no selected quizpool or quiztask is provided,
    it will return the first objects from the database.

    :param selected_pool: The selected quizpool object (default: None)
    :param selected_task: The selected quiztask object (default: None)
    :return: A dictionary containing the quiz pools, quiz tasks, selected pool and selected task

    Example usage:
    content = get_library_content(selected_pool=my_selected_pool, selected_task=my_selected_task)
    """

    # Fetch all quiz pool objects
    quizpools = QuizPool.objects.all()
    quiztasks = None

    # If quiz pool objects exist
    if quizpools.exists():
        # If no specific pool is selected, choose the first one
        if not selected_pool:
            selected_pool = quizpools.first()

        # Fetch quiz task objects for the selected pool
        quiztasks = QuizTask.objects.filter(pool_id=selected_pool.id)

        # If quiz task objects exist
        if quiztasks.exists():
            # If no specific task is selected, choose the first one
            if not selected_task:
                selected_task = quiztasks.first()

    # Return a dictionary containing all the objects
    return {'quizpools': quizpools,
            'quiztasks': quiztasks,
            'selected_pool': selected_pool,
            'selected_task': selected_task}

def show_library(request):
    """
    Renders the complete library by rendering the 'library.html' template with the library content.

    :param request: The HTTP request object from the client

    :return: A rendered HTTP response of the library.
    """

    return render(request, 'library/library.html', get_library_content())

#
# QuizPools
#

def create_quizpool(request):
    """
    Creates a quizpool entity in the database.

    Parameters:
    :param request: The HTTP request object.

    :return: A rendered HTTP response of the library content.
    """

    if request.method == 'POST':
        quizpool_form = QuizPoolForm(request.POST)
        if quizpool_form.is_valid():
            quizpool = quizpool_form.save(commit=False)
            quizpool.creator = request.user
            quizpool.save()

    quizpools = QuizPool.objects.all()
    return render(request, 'library/library-content.html',
                  get_library_content(selected_pool=quizpools.last()))

def change_quizpool_name(request, pool_id:int):
    """
    Changes the name of a selected quiz pool.

    :param request: The HTTP request object.
    :param pool_id: The ID of the quiz pool to be changed.

    :return: HttpResponse: Renders the fully updated library (through library-content.html) with the
        changed quiz pool as the selected one.
    """

    selected_pool = QuizPool.objects.get(id=pool_id)
    # Check if the user is the creator of the QuizPool or belongs to the 'dozent' group
    user_groups = Group.objects.filter(user=request.user)
    if request.user == selected_pool.creator or user_groups.filter(name='dozent').exists():
        # Check that the request's form data is valid, but this validation isn't used for further processing
        if (QuizPoolForm(request.POST).is_valid()):
            # Retrieve the specific QuizPool from the database, Update it's name and save it back to the database

            selected_pool.name = request.POST.get('name', None)
            selected_pool.save()

    # Render the updated library content with the specified quiz pool's name changed
    return render(request, 'library/library-content.html',
                  get_library_content(selected_pool=selected_pool))

def delete_quizpool(request, pool_id:int):
    """
    Delete QuizPool

    Deletes a QuizPool from the database if the user is the creator of the QuizPool or belongs to the 'dozent' group.

    :param request: The HTTP request object.
    :param pool_id: The ID of the QuizPool to be deleted.

    :returns: HttpResponse: The rendered HTML response of the library content page.
    """
    pool = QuizPool.objects.get(id=pool_id)

    # Check if the user is the creator of the QuizPool or belongs to the 'dozent' group
    user_groups = Group.objects.filter(user=request.user)
    if request.user == pool.creator or user_groups.filter(name='dozent').exists():
        pool.delete()

    return render(request, 'library/library-content.html', get_library_content())

#
# QuizTasks
#
def show_quiztasks(request, pool_id:int):
    """
    Display the quiz tasks for a given quiz pool.

    :param request: The HTTP request that triggered the view.
    :param pool_id: The ID of the quiz pool.

    Returns:
        The rendered template 'library/quiztasks.html' with the following context:
        - quiztasks: The list of quiz tasks for the specified pool.
        - selected_pool: The selected quiz pool object.

    Raises:
        QuizPool.DoesNotExist: If the specified quiz pool does not exist in the database.
    """

    quiztasks = QuizTask.objects.filter(pool_id=pool_id)
    selected_pool = QuizPool.objects.get(id=pool_id)

    return render(request, 'library/quiztasks.html',
                  {'quiztasks': quiztasks,
                   'selected_pool': selected_pool, })


#@permission_required("Library.add_quiztask", login_url='/login', raise_exception=True)
def create_quiztask(request, pool_id:int):
    """
    Create a quiz task for a specific quiz pool.

    :param request: The HTTP request object.
    :param pool_id: An integer representing the ID of the quiz pool.
    :return: Rendered template 'library/quiztasks.html' with context variables.

    """
    selected_pool = QuizPool.objects.get(id=pool_id)

    # Save form data, assign current user as creator, and specific QuizPool to the QuizTask
    if request.method == 'POST':
        form = QuizTaskForm(request.POST)

        if form.is_valid():
            quiztask = form.save(commit=False)
            quiztask.creator = request.user
            quiztask.pool = selected_pool
            quiztask.save()

    # Query for QuizTask objects for the pool, and render the template with the
    # queried objects and the specific QuizPool
    quiztasks = QuizTask.objects.filter(pool_id=pool_id)
    return render(request, 'library/quiztasks.html',
                  {'quiztasks': quiztasks,
                   'selected_pool': selected_pool,})

def change_question(request, task_id:int):
    """
    Change the question of a quiz task.

    :param request: The HTTP request object.
    :param task_id: The ID of the quiz task to be updated.

    The method fetches the selected quiz task based on the given task ID.
    It then checks if the user is the creator of the quiz pool or belongs to the 'dozent' group.
    If the user has the necessary permissions and the provided form data is valid, the method updates the question of the selected quiz task with the new question text obtained from the request.
    Finally, it fetches the quiz pool related to the updated quiz task and renders the updated full library with the changed quiz pool and quiz task.

    :return: Rendered template 'library/library-content.html' with context variables.
    """
    # Fetch the selected QuizTask
    selected_task = QuizTask.objects.get(id=task_id)

    # Check if the user is the creator of the QuizPool or belongs to the 'dozent' group
    user_groups = Group.objects.filter(user=request.user)
    if request.user == selected_task.creator or user_groups.filter(name='dozent').exists():
        # Check whether form data is valid
        if QuizTaskForm(request.POST).is_valid():
            # If valid, fetch the new question text from the request and update the selected QuizTask
            new_question = request.POST.get('question', None)
            selected_task.question = new_question
            selected_task.save()

    # Fetch the QuizPool related to the updated QuizTask and render updated full library with
    # changed Quizpool and QuizTask
    selected_pool = QuizPool.objects.get(id=selected_task.pool_id)
    return render(request, 'library/library-content.html',
                  get_library_content(selected_pool=selected_pool, selected_task=selected_task))

def delete_quiztask(request, task_id:int):
    """
    Delete Quiz Task.

    This method is used to delete a quiz task from the system.

    :param request: The request object for the current HTTP request.
    :param task_id: The ID of the quiz task to be deleted.

    :returns: HttpResponse: The rendered response with the updated library content.
    """
    selected_task  = QuizTask.objects.get(id=task_id)
    # Check if the user is the creator of the QuizPool or belongs to the 'dozent' group
    user_groups = Group.objects.filter(user=request.user)
    if request.user == selected_task.creator or user_groups.filter(name='dozent').exists():
        selected_task.delete()

    return render(request, 'library/library-content.html', get_library_content())

#
# Answers
#
def get_answers(task_id:int):
    """
    Get the answers for a given task.

    :param task_id: The ID of the task.

    :return: List[Answer]: The list of answers for the given task.
    """
    answers = Answer.objects.filter(task_id=task_id)

    return answers

def show_answers(request, task_id:int):
    """
        Retrieve and render answers related to a specific QuizTask identified by task_id.

        :param request: The HTTP request object.
        :param task_id: An integer that represents the ID of the QuizTask.
        :return: A HttpResponse that renders HTML template 'library/answers.html' with QuizTask answers.
        """

    # Fetch answers related to the QuizTask specified by task_id
    answers = get_answers(task_id=task_id)

    # Fetch the specific QuizTask instance
    selected_task = QuizTask.objects.get(id=task_id)

    # Render the HTML page with the fetched answers and the specific QuizTask instance
    return render(request, 'library/answers.html',
                  {'answers': answers, 'selected_task': selected_task})

def create_answer(request, task_id:int):
    """
    Create an answer for a given task.

    :param request: The Django Request object.
    :param task_id: The ID of the task to create an answer for.

    Behavior:
        - Fetches the QuizTask object with the given task_id.
        - Handles POST request:
            - Validates the form.
            - Creates a new Answer instance and sets the creator and task fields.
            - Saves the answer to the database.
        - Fetches the QuizTask object and related answers.
        - Renders the 'library/answers.html' template with the answers and selected_task.

    :return: A HttpResponse that renders HTML template 'library/answers.html' with QuizTask answers.
    """

    selected_task = QuizTask.objects.get(id=task_id)

    # Handle POST request: Validate form, create new Answer instance, save to DB
    if request.method == 'POST':
        form = AnswerForm(request.POST)

        if form.is_valid():
            answer = form.save(commit=False)
            answer.creator = request.user
            answer.task = selected_task
            answer.save()

    # Fetch QuizTask instance and related answers, render 'library/answers.html'
    answers = Answer.objects.filter(task_id=task_id)
    selected_task = QuizTask.objects.get(id=task_id)
    return render(request, 'library/answers.html',
                  {'answers': answers,
                   'selected_task': selected_task})

def edit_answer(request, answer_id:int):
    """
       Edit the data of an Answer entity in the database using the AnswerForm.

       :param request: the Django HttpRequest object that carries all the
                                  details about the current webpage request from user.
       :param answer_id: ID of the Answer that is to be updated.

       :return: HttpResponse: Renders the updated answer column of the library (answers.html).
            Also returns the selected QuizTask object for further processing.
       """
    answer = Answer.objects.get(id=answer_id)
    selected_task = QuizTask.objects.get(id=answer.task_id)

    # Check if the user is the creator of the QuizPool or belongs to the 'dozent' group
    user_groups = Group.objects.filter(user=request.user)
    if request.user == selected_task.creator or user_groups.filter(name='dozent').exists():

        # Handle POST request: Validate form, make changes to the Answer instance, save to DB
        if (AnswerForm(request.POST).is_valid()):
            # This form is not processed further, but only to validate the passed 'question'.
            answer.answer = request.POST.get('answer', None)
            answer.explanation = request.POST.get('explanation', None)
            answer.correct = request.POST.get('correct', 'False')
            answer.save()

            # Get all answers that relate to the current task and render the updated answer column of the library
            answers = Answer.objects.filter(task_id=answer.task_id)
            selected_task = QuizTask.objects.get(id=answer.task_id)
            return render(request, 'library/answers.html',
                          {'answers': answers,
                           'selected_task': selected_task,})

def delete_answer(request, answer_id:int):
    """
    Delete the selected Answer record from the database.

    :param request: the Django HttpRequest object that carries all the
                               details about the current webpage request from user.
    :param answer_id: ID of the Answer record to delete from the database.

    :return: HttpResponse: Renders the updated answer column of the library (answers.html).
                      In addition, it returns the selected QuizTask object for further processing.
    """
    # Get the task_id for returning the selected QuizTask
    task_id = Answer.objects.get(id=answer_id).task_id
    selected_task = QuizTask.objects.get(id=task_id)

    # Check if the user is the creator of the QuizPool or belongs to the 'dozent' group
    user_groups = Group.objects.filter(user=request.user)
    if request.user == selected_task.creator or user_groups.filter(name='dozent').exists():
        # Delete the Answer record from the database
        Answer.objects.get(id=answer_id).delete()

    # Get all answers that relate to the current task and render the updated answer column of the library
    answers = Answer.objects.filter(task_id=task_id)
    selected_task = QuizTask.objects.get(id=task_id)
    return render(request, 'library/answers.html',
                  {'answers': answers,
                   'selected_task': selected_task})