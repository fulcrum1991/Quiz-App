from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages import get_messages
from django.core.checks import messages
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
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
            update_session_auth_hash(request, user)  #Nutzer bleibt auch nach dem Ändern der Daten eingeloggt
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
            messages.success(request, 'Login erfolgreich!')

            # Neuladen der Navbar, um Nutzernamen anzuzeigen
            response = HttpResponse(f'''
                <ul class="navbar-nav" hx-swap-oob="true" id="user-navbar">
                    <li class="nav-item">
                        <span class="navbar-text">Eingeloggt als {user.username}</span>
                    </li>
                    <li class="nav-item">
                        <form method="post" action="{request.build_absolute_uri('/logout/')}">
                            <input type="hidden" name="csrfmiddlewaretoken" value="{request.META['CSRF_COOKIE']}">
                            <button type="submit" class="btn btn-link nav-link">Logout</button>
                        </form>
                    </li>
                </ul>
            ''')
            response['HX-Redirect'] = '/library'

            # Aufruf der Messages, um fehlerhafte Anzeige nach Navigation zu vermeiden
            list(get_messages(request))

            return response

        else:
            messages.error(request, 'Ungültige Anmeldedaten.')

            # Prüfen, ob HTMX Request ausgelöst wurde
            if request.headers.get('HX-Request'):
                # Aufruf der Fehlermeldung, um fehlerhafte Anzeige nach Navigation zu vermeiden
                error_messages = list(get_messages(request))

                # Nur Rückgabe der Fehlermeldung
                return HttpResponse('<div class="alert alert-danger">Ungültige Anmeldedaten.</div>')

            # Non-HTMX fallback
            return redirect('/login')

    return HttpResponse('Ungültige Anfrage.', status=400)


def register_htmx(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Prüfen, ob die eingegebenen Passwörter übereinstimmen
        if password1 != password2:
            messages.error(request, 'Passwörter stimmen nicht überein.')

            if request.headers.get('HX-Request'):
                # Consume messages
                error_messages = list(get_messages(request))
                # Nur Rückgabe der Fehlermeldung
                return HttpResponse('<div class="alert alert-danger">Passwörter stimmen nicht überein.</div>')

            # Non-HTMX fallback
            return redirect('/register')

        # Prüfen, ob Nutzername bereits vergeben ist
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Benutzername bereits vergeben.')

            if request.headers.get('HX-Request'):
                error_messages = list(get_messages(request))
                return HttpResponse('<div class="alert alert-danger">Benutzername bereits vergeben.</div>')

            return redirect('/register')

        # Prüfen, ob E-Mail bereits registriert ist
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email bereits registriert.')

            if request.headers.get('HX-Request'):
                error_messages = list(get_messages(request))
                return HttpResponse('<div class="alert alert-danger">Email bereits registriert.</div>')

            return redirect('/register')

        # Anlegen eines neuen Nutzers bei Registrierung
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()

            # Benutzer nach erfolgreicher Anmeldung einloggen
            login(request, user)
            messages.success(request, 'Registrierung erfolgreich!')

            # Neuladen der Navbar, um Usernamen anzuzeigen
            response = HttpResponse(f'''
                <ul class="navbar-nav" hx-swap-oob="true" id="user-navbar">
                    <li class="nav-item">
                        <span class="navbar-text">Eingeloggt als {user.username}</span>
                    </li>
                    <li class="nav-item">
                        <form method="post" action="{request.build_absolute_uri('/logout/')}">
                            <input type="hidden" name="csrfmiddlewaretoken" value="{request.META['CSRF_COOKIE']}">
                            <button type="submit" class="btn btn-link nav-link">Logout</button>
                        </form>
                    </li>
                </ul>
            ''')

            response['HX-Redirect'] = '/library'

            # Aufruf der Messages, um fehlerhafte Anzeige nach Navigation zu vermeiden
            list(get_messages(request))

            return response

        except ValidationError as e:
            messages.error(request, str(e))

            if request.headers.get('HX-Request'):
                error_messages = list(get_messages(request))
                return HttpResponse(f'<div class="alert alert-danger">{str(e)}</div>')

            return redirect('/register')

    # Fehlermeldung bei Ungültiger Anfrage
    return HttpResponseBadRequest('Ungültige Anfrage.')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})  #Ermöglicht Navigation, wenn angemeldet


@login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Überprüfung, ob alle Felder ausgefüllt sind
        if not username or not email:
            messages.error(request, 'Bitte füllen Sie alle Felder aus.')

            # Überprüfung, ob es sich um eine HTMX-Anfrage handelt
            if request.headers.get('HX-Request'):
                # Fehlernachricht ausgeben und konsumieren
                error_messages = list(get_messages(request))
                return HttpResponse('<div class="alert alert-danger">Bitte füllen Sie alle Felder aus.</div>')

            # Nicht-HTMX-Anfrage: Umleitung zur Bearbeitungsseite
            return redirect('edit_profile')

        # Profildaten aktualisieren
        request.user.username = username
        request.user.email = email
        request.user.save()

        messages.success(request, 'Profildaten erfolgreich geändert!')

        # Überprüfung, ob es sich um eine HTMX-Anfrage handelt
        if request.headers.get('HX-Request'):
            # Erfolgsnachricht ausgeben und Navbar aktualisieren
            response = HttpResponse(f'''
                <div class="alert alert-success">Profildaten erfolgreich geändert!</div>
                <ul class="navbar-nav" hx-swap-oob="true" id="user-navbar">
                    <li class="nav-item">
                        <span class="navbar-text">Eingeloggt als {request.user.username}</span>
                    </li>
                    <li class="nav-item">
                        <form method="post" action="{request.build_absolute_uri('/logout/')}">
                            <input type="hidden" name="csrfmiddlewaretoken" value="{request.META['CSRF_COOKIE']}">
                            <button type="submit" class="btn btn-link nav-link">Logout</button>
                        </form>
                    </li>
                </ul>
            ''')

            # Nachrichten konsumieren, um sie aus der Session zu entfernen
            list(get_messages(request))
            return response

        # Nicht-HTMX-Anfrage: Erfolgsnachricht anzeigen und zur Bearbeitungsseite zurückkehren
        return render(request, 'accounts/profile_edit_form.html', {
            'user': request.user,
            'hx_trigger': 'updateNavbar'
        })

    # Rendern des Profilbearbeitungsformulars für GET-Anfragen
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
                return redirect('profile')  #Wenn Nutzerdaten korrekt -> Weiterleitung auf Profil
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})  #Wenn request für Login -> Laden von Login


def logout_view(request):
    logout(request)
    return redirect('login')  #Wenn Logout-Button betätigt -> Abmeldung


@login_required
def update_navbar(request):
    return render(request, 'base.html')
