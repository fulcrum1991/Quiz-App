from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.checks import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .forms import SignUpForm, CustomPasswordChangeForm, UserUpdateForm, DeleteUserForm

# Create your views here.
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/sign-up.html', {'form': form})

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

def login_htmx(request):  #Funktion, um Login mit HTMX zu ermöglichen
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login erfolgreich!'}, status=200)       #Wenn Nutzerdaten korrekt -> Anmeldung
        else:
            return JsonResponse({'message': 'Ungültige Anmeldedaten.'}, status=400)  #Wenn Nutzerdaten inkorrekt -> Meldung
    return JsonResponse({'message': 'Ungültige Anfrage.'}, status=400) #Wenn ungültige Anfrage -> Fehlermeldung


def register_htmx(request): #Funktion, um Registrierung mit HTMX zu ermöglichen
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        role = request.POST['role']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            return JsonResponse({'message': 'Passwörter stimmen nicht überein.'}, status=400) #Meldung bei falschen Passwort

        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Benutzername bereits vergeben.'}, status=400) #Meldung, wenn Name bereits vergeben

        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email bereits registriert.'}, status=400) #Meldung, wenn E-Mail bereits vergeben

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            # Rollenzugehörigkeit ggf. ergänzen
            user.save()
            return JsonResponse({'message': 'Registrierung erfolgreich!'}, status=200) #Wenn Daten erfolgreich abgeglichen -> Pass
        except ValidationError as e:
            return JsonResponse({'message': str(e)}, status=400)

    return JsonResponse({'message': 'Ungültige Anfrage.'}, status=400) #Wenn fehlerhafte Anfrage -> Error


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        if not username or not email:
            return JsonResponse({'message': 'Bitte füllen Sie alle Felder aus.'}, status=400)

        request.user.username = username
        request.user.email = email
        request.user.save()

        return JsonResponse({'message': 'Profildaten erfolgreich geändert!'}, status=200)

    return render(request, 'accounts/profile_edit_form.html', {'user': request.user})

@login_required
@require_http_methods(["POST"])
def delete_profile(request):
    request.user.delete()
    return JsonResponse({'message': 'Profil erfolgreich gelöscht!'}, status=200)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')