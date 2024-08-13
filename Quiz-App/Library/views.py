from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods

from .forms import QuizPoolForm, QuizTaskForm, AnswerForm
from .models import QuizPool, QuizTask, Answer



# Create your views here.

def get_library_content(selected_pool=None, selected_task = None):
    # Ruft Quizpool und Quiztask Objekte aus der Datenbank ab und gibt diese in einem Dictionary zurück,
    # um von anderen Funktion für das Rendern der library genutzt zu werden. Zusätzlich werden das
    # aktuell ausgewählte Quizpool und Quiztask (welche vorher übergeben werden), oder das jeweils erste
    # Objekt der Datenbank zurückgegeben.

    quizpools = QuizPool.objects.all()
    quiztasks = None

    if bool(quizpools):
        if not selected_pool:
            selected_pool = quizpools.first()

        quiztasks = QuizTask.objects.filter(pool_id=selected_pool.id)
        if bool(quiztasks):
            if not selected_task:
                selected_task = QuizTask.objects.first()

    return {'quizpools': quizpools,
            'quiztasks': quiztasks,
            'selected_pool': selected_pool,
            'selected_task': selected_task}

def library(request):
    # Rückgabe: Rendert die vollständige Bibliothek (library.html)
    return render(request, 'library/library.html', get_library_content())

#
# QuizPools
#

#@permission_required("Library.add_quiztask", login_url='/login', raise_exception=True)
def create_quizpool(request):
    # Erstellt neue Quizpool-Entität in der DB mithilfe der QuizPoolForm.
    # Rückgabe: Rendert die aktualisierte Bibliothek vollständig (durch library-content.html) mit diesem
    # zuletzt erstellten Quizpool als ausgewählten Quizpool.

    if request.method == 'POST':
        quizpool_form = QuizPoolForm(request.POST)
        if quizpool_form.is_valid():
            quizpool = quizpool_form.save(commit=False)
            quizpool.creator = request.user
            quizpool.save()

    quizpools = QuizPool.objects.all()
    return render(request, 'library/library-content.html',
                  get_library_content(selected_pool=quizpools.last()))

def change_quizpool_name(request, pool_id):
    # Ändert den Namen eines ausgewählten Quizpools.
    # Übergabe: ID des zu ändernden Quizpools.
    # Rückgabe: Rendert die aktualisierte Bibliothek vollständig (durch library-content.html) mit diesem
    # geänderten Quizpool als ausgewählten Quizpool.

    if(QuizPoolForm(request.POST).is_valid()):
        # Diese Form wird nicht weiterverarbeitet, sondern nur genutzt, um den Namen zu validieren
        quizpool = QuizPool.objects.get(id=pool_id)
        new_name = request.POST.get('name', None)
        quizpool.name = new_name
        quizpool.save()

    selected_pool = QuizPool.objects.get(id=pool_id)
    return render(request, 'library/library-content.html',
                  get_library_content(selected_pool=selected_pool))

def delete_quizpool(request, pool_id):
    # Löscht den ausgewählten Quizpools.
    # Übergabe: ID des zu löschenden Quizpools.
    # Rückgabe: Rendert die aktualisierte Bibliothek vollständig (durch library-content.html).

    QuizPool.objects.get(id=pool_id).delete()

    return render(request, 'library/library-content.html', get_library_content())

#
# QuizTasks
#
def get_quiztasks(request, pool_id):
    # Übergabe: ID des Quizpools, dessen Quiztasks angezeigt werden sollen.
    # Rückgabe: Rendert die Quiztask-Spalte der Bibliothek (quiztasks.html). Zusätzlich wird das ausgewählte
    # Quizpool-Objekt für die weitere Verarbeitung zurückgegeben.

    quiztasks = QuizTask.objects.filter(pool_id=pool_id)
    selected_pool = QuizPool.objects.get(id=pool_id)

    return render(request, 'library/quiztasks.html',
                  {'quiztasks': quiztasks,
                   'selected_pool': selected_pool,})


#@permission_required("Library.add_quiztask", login_url='/login', raise_exception=True)
def create_quiztask(request, pool_id):
    # Erstellt neue Quiztask-Entität in der DB mithilfe der QuizTaskForm.
    # Übergabe: ID des Quizpools, dem der Quiztasks hinzugefügt werden soll.
    # Rückgabe: Rendert die aktualisierte Quiztask-Spalte der Bibliothek (quiztasks.html). Zusätzlich wird
    # das ausgewählte Quizpool-Objekt für die weitere Verarbeitung zurückgegeben.

    if request.method == 'POST':
        form = QuizTaskForm(request.POST)

        if form.is_valid():
            quiztask = form.save(commit=False)
            quiztask.creator = request.user
            quiztask.pool = QuizPool.objects.get(id=pool_id)
            quiztask.save()

    quiztasks = QuizTask.objects.filter(pool_id=pool_id)
    selected_pool = QuizPool.objects.get(id=pool_id)
    return render(request, 'library/quiztasks.html',
                  {'quiztasks': quiztasks,
                   'selected_pool': selected_pool})

def change_question(request, task_id):
    # Ändert den Namen eines ausgewählten Quiztasks.
    # Übergabe: ID des zu ändernden Quiztasks.
    # Rückgabe: Rendert die aktualisierte Bibliothek vollständig (durch library-content.html) mit diesem
    # geänderten Quizpool als ausgewählten Quizpool.

    selected_task = QuizTask.objects.get(id=task_id)

    if(QuizTaskForm(request.POST).is_valid()):
        # Diese Form wird nicht weiterverarbeitet, sondern nur genutzt, um die übergebene 'question' zu validieren.
        new_question = request.POST.get('question', None)
        selected_task.question = new_question
        selected_task.save()

    selected_pool = selected_task.pool_id

    return render(request, 'library/library-content.html',
                  get_library_content(selected_pool=selected_pool, selected_task=selected_task))

def delete_quiztask(request, task_id):
    # Löscht den ausgewählten Quiztask.
    # Übergabe: ID des zu löschenden Quiztasks.
    # Rückgabe: Rendert die aktualisierte Bibliothek vollständig (durch library-content.html).

    QuizTask.objects.get(id=task_id).delete()

    return render(request, 'library/library-content.html', get_library_content())

#
# Answers
#
def get_answers(request, task_id):
    # Übergabe: ID des Quiztasks, dessen Answers angezeigt werden sollen.
    # Rückgabe: Rendert die Antwort-Spalte der Bibliothek (answers.html). Zusätzlich wird das ausgewählte
    # Quiztask-Objekt für die weitere Verarbeitung zurückgegeben.

    answers = Answer.objects.filter(task_id=task_id)
    selected_task = QuizTask.objects.get(id=task_id)

    return render(request, 'library/answers.html',
                  {'answers': answers,
                   'selected_task': selected_task})

def create_answer(request, task_id):
    # Erstellt neue Quiztask-Entität in der DB mithilfe der AnswerForm.
    # Übergabe: ID des Quiztasks, dem die Answer hinzugefügt werden soll.
    # Rückgabe: Rendert die aktualisierte Antwort-Spalte der Bibliothek (answers.html). Zusätzlich wird das
    # ausgewählte Quiztask-Objekt für die weitere Verarbeitung zurückgegeben.

    if request.method == 'POST':
        form = AnswerForm(request.POST)

        if form.is_valid():
            answer = form.save(commit=False)
            answer.creator = request.user
            answer.task = QuizTask.objects.get(id=task_id)
            answer.save()

    answers = Answer.objects.filter(task_id=task_id)
    selected_task = QuizTask.objects.get(id=task_id)
    return render(request, 'library/answers.html',
                  {'answers': answers,
                   'selected_task': selected_task})

def edit_answer(request, answer_id):
    # Editiert die Daten einer Answer-Entität in der DB mithilfe der AnswerForm.
    # Übergabe: ID der Answer, die geändert werden soll.
    # Rückgabe: Rendert die aktualisierte Antwort-Spalte der Bibliothek (answers.html). Zusätzlich wird das
    # ausgewählte Quiztask-Objekt für die weitere Verarbeitung zurückgegeben.

    if (AnswerForm(request.POST).is_valid()):
        # Diese Form wird nicht weiterverarbeitet, sondern nur genutzt, um die übergebene 'question' zu validieren.
        answer = Answer.objects.get(id=answer_id)
        answer.answer = request.POST.get('answer', None)
        answer.hint = request.POST.get('hint', None)
        answer.correct = request.POST.get('correct', 'False')
        answer.save()

        answers = Answer.objects.filter(task_id=answer.task_id)
        selected_task = QuizTask.objects.get(id=answer.task_id)
        return render(request, 'library/answers.html',
                      {'answers': answers,
                       'selected_task': selected_task,})

def delete_answer(request, answer_id):
    # Löscht die ausgewählte Answer.
    # Übergabe: ID der zu löschenden Answer.
    # Rückgabe: Rendert die aktualisierte Antwort-Spalte der Bibliothek (answers.html). Zusätzlich wird das
    # ausgewählte Quiztask-Objekt für die weitere Verarbeitung zurückgegeben.

    task_id = Answer.objects.get(id=answer_id).task_id
    # Abfragen der task_id für die Rückgabe der ausgwählten Quiztask

    Answer.objects.get(id=answer_id).delete()

    answers = Answer.objects.filter(task_id=task_id)
    selected_task = QuizTask.objects.get(id=task_id)
    return render(request, 'library/answers.html',
                  {'answers': answers,
                   'selected_task': selected_task})