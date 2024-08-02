from django.contrib.auth import update_session_auth_hash, logout
from django.core.checks import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse

from .forms import QuizTaskForm, SignUpForm, CustomPasswordChangeForm, UserUpdateForm, DeleteUserForm
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
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(request.user, request.POST)

        if user_form.is_valid() and password_form.is_valid():
            user_form.save()
            user = password_form.save()
            update_session_auth_hash(request, user) #Nutzer bleibt auch nach dem Ändern der Daten eingeloggt
            return redirect('profile')

@login_required
def delete_profile(request):
    if request.method == 'POST':
        form = DeleteUserForm(request.POST)
        if form.is_valid() and form.cleaned_data['confirm']:
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Ihr Profil wurde erfolgreich gelöscht.')
            return HttpResponseRedirect(reverse('home'))
    else:
        form = DeleteUserForm()

    return render(request, 'accounts/delete_profile.html', {'form': form})

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

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'sign-up.html', {'form': form})


