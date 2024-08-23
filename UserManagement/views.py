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
from django.contrib import messages
from django.shortcuts import redirect

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

def login_htmx(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login erfolgreich!')  # Erfolgreiche Anmeldung

            # Redirect zur Library-Seite und Triggern des Navbar-Updates
            return render(request, 'library/library.html', {
                'hx_trigger': 'updateNavbar'
            })
        else:
            messages.error(request, 'Ungültige Anmeldedaten.')  # Fehlermeldung bei ungültigen Anmeldedaten
            return redirect('accounts/login')  # Umleitung zurück zur Login-Seite

    messages.error(request, 'Ungültige Anfrage.')  # Fehlermeldung bei ungültiger Anfrage
    return redirect('accounts/login')  # Umleitung zurück zur Login-Seite


def register_htmx(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        role = request.POST['role']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, 'Passwörter stimmen nicht überein.')  # Meldung bei falschen Passwort
            return redirect('accounts/sign-up')  # Umleitung zurück zur Registrierungsseite

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Benutzername bereits vergeben.')  # Meldung, wenn Name bereits vergeben
            return redirect('accounts/sign-up')  # Umleitung zurück zur Registrierungsseite

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email bereits registriert.')  # Meldung, wenn E-Mail bereits vergeben
            return redirect('accounts/sign-up')  # Umleitung zurück zur Registrierungsseite

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            login(request, user)  # Der Benutzer wird automatisch eingeloggt nach der Registrierung
            messages.success(request, 'Registrierung erfolgreich!')  # Erfolgreiche Registrierung
            return render(request, 'library/library.html', {
                'user': user,
                'hx_trigger': 'updateNavbar'
            })
        except ValidationError as e:
            messages.error(request, str(e))  # Fehlermeldung bei ValidationError
            return redirect('accounts/sign-up')  # Umleitung zurück zur Registrierungsseite

    messages.error(request, 'Ungültige Anfrage.')  # Meldung bei ungültiger Anfrage
    return redirect('accounts/sign-up')  # Umleitung zurück zur Registrierungsseite


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user}) #Ermöglicht Navigation, wenn angemeldet

@login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        if not username or not email:
            messages.error(request, 'Bitte füllen Sie alle Felder aus.')  # Fehler, wenn Felder leer sind
            return redirect('edit_profile')  # Umleitung zurück zum Bearbeitungsformular

        # Profildaten aktualisieren
        request.user.username = username
        request.user.email = email
        request.user.save()

        messages.success(request, 'Profildaten erfolgreich geändert!')  # Erfolgreiche Aktualisierung

        # Rückgabe der aktualisierten Seite und Triggern des Navbar-Updates
        return render(request, 'accounts/profile_edit_form.html', {
            'user': request.user,
            'hx_trigger': 'updateNavbar'
        })

    # Rendern des Profilbearbeitungsformulars
    return render(request, 'accounts/profile_edit_form.html', {'user': request.user})


@login_required
@require_http_methods(["POST"])
def delete_profile(request):
    # Benutzerprofil löschen
    request.user.delete()

    # Erfolgsmeldung
    messages.success(request, 'Profil erfolgreich gelöscht!')

    # Weiterleitung zur Startseite nach dem Löschen und Triggern des Navbar-Updates
    return redirect('home')  # Gehe zur Startseite oder zu einer anderen Zielseite

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile') #Wenn Nutzerdaten korrekt -> Weiterleitung auf Profil
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form}) #Wenn request für Login -> Laden von Login

def logout_view(request):
    logout(request)
    return redirect('login') #Wenn Logout-Button betätigt -> Abmeldung

@login_required
def update_navbar(request):
    return render(request, 'base.html')