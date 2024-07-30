from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .forms import QuizTaskForm
from .models import QuizTask
# Create your views here.

#@login_required(login_url='/login')                  # Change. Lesender Zugriff auf Bibliothek soll gegeben sein
def library(request):
    quiztasks = QuizTask.objects.all()

    # Delete a quiztask
    if request.method == 'POST':
        quiztask_id = request.POST.get('quiztask-id')
        quiztask = QuizTask.objects.filter(id=quiztask_id).first()
        if quiztask and (quiztask.author == request.user or request.user.has_perm('quiz.delete_quiztask', quiztask)):
            quiztask.delete()

    return render(request, 'library.html', {'quiztasks': quiztasks})

@login_required(login_url='/login')
@permission_required("Library.add_quiztask", login_url='/login', raise_exception=True)
def create_quiztask(request):                       # naming convention pep8
    if request.method == 'POST':
        form = QuizTaskForm(request.POST)
        if form.is_valid():
            quiztask = form.save(commit=False)
            quiztask.author = request.user
            quiztask.save()
            return redirect('library')
    else:
        form = QuizTaskForm()

    return render(request, 'create-quiztask.html', {'form': form})

