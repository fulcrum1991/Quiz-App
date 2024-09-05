from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages import get_messages
from django.core.checks import messages
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
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
    """
    Registers a new user with the given request data.

    :param request (HttpRequest): The HTTP request object containing the user sign up data.

    """
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
    """
    Profile Method

    This method is responsible for handling the profile page for logged-in users. It requires a logged-in user to
    access and can be used in conjunction with the `@login_required` decorator.

    :param request: The HTTP request object.

    :returns: If the HTTP request method is 'POST' and both the user form and password form are valid, this method
    saves the user's updated information and changes the user's password (if provided). It then updates the session
    authentication hash to keep the user logged in. Finally, it redirects the user to the profile page.
    """
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
    """
    Deletes the user's profile.

    This method requires the user to be logged in. If the request method is POST,
    the method validates the form data and if the "confirm" field is set to True,
    the user's profile is deleted. The method then logs out the user, displays a
    success message and redirects the user to the home page.

    :param request: The HTTP request object.

    :returns: HttpResponseRedirect: A response that redirects the user to the home page.
    """
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
    """
    Logs in a user using HTMX request.

    :param request: The HTTP request object.

    :returns: If the request method is 'POST' and the authentication is successful, it returns an HTTP response that includes a success message and a refreshed navigation bar with the logged-in username. The response also includes a header for HTMX redirection to the '/library' page.
    - If the authentication fails, it returns an HTTP response with an error message. If the request is an HTMX request, it only returns the error message as a HTML div. Otherwise, it redirects to the '/login' page.
    - If the request method is not 'POST', it returns an HTTP response with a "Bad Request" status and a message indicating an invalid request.
    """
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
    """
    Registers a user with HTMX capabilities.

    Args:
        request (HttpRequest): The HTTP request object.

    :returns: HttpResponse or None: The HTTP response object or None.
    """
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
    """
    This function is used to render the user's profile page.

    :param request: The HTTP request object.
    """
    return render(request, 'accounts/profile.html', {'user': request.user})  #Ermöglicht Navigation, wenn angemeldet


@login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    """
    Edit the user profile.

    This method is decorated with `@login_required` and `@require_http_methods(["GET", "POST"])` to ensure that the user
    is authenticated and that only GET and POST requests are allowed.

    :param request: The request object sent by the client.

    Returns:
    - If the request method is POST and the profile data is successfully updated, the method may return an HttpResponse
    object with a success message if the request header contains 'HX-Request'. In this case, an HTTP response with an
    HTML div containing the success message is returned.
    - If the request method is POST and the profile data is not valid (missing fields or invalid password change form),
    the method may return an HttpResponse object with an error message if the request header contains 'HX-Request'.
    In this case, an HTTP response with an HTML div containing the error message is returned.
    - If the request method is POST and the profile data is valid but the password change form is not filled or not
    valid, the method may return an HttpResponse object with an error message if the request header contains
    'HX-Request'. In this case, an HTTP response with an HTML div containing the error message is returned.
    - If the request method is GET, the method returns a rendered template 'accounts/profile_edit_form.html' with the
    following context variables:

        - 'user': The currently authenticated user.
        - 'password_change_form': An instance of CustomPasswordChangeForm for changing the user's password.

    Note: The `CustomPasswordChangeForm` is a custom form used for password changes.

    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Überprüfen, ob die Profildaten leer sind
        if not username or not email:
            messages.error(request, 'Bitte füllen Sie alle Felder aus.')

            if request.headers.get('HX-Request'):
                error_messages = list(get_messages(request))
                return HttpResponse('<div class="alert alert-danger">Bitte füllen Sie alle Felder aus.</div>')
            return redirect('edit_profile')

        # Profildaten aktualisieren
        request.user.username = username
        request.user.email = email
        request.user.save()

        # Passwortänderungsformular initialisieren
        password_change_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        # Überprüfen, ob das Passwortänderungsformular ausgefüllt und gültig ist
        if password_change_form.is_valid():
            # Passwort ändern und die Session aktualisieren
            user = password_change_form.save()
            update_session_auth_hash(request, user)  # Wichtig, damit die Sitzung erhalten bleibt
            messages.success(request, 'Passwort erfolgreich geändert!')

            if request.headers.get('HX-Request'):
                response = HttpResponse('<div class="alert alert-success">Passwort erfolgreich geändert!</div>')
                list(get_messages(request))
                return response
        elif any([request.POST.get('old_password'), request.POST.get('new_password1'), request.POST.get('new_password2')]):
            # Wenn eines der Passwortfelder ausgefüllt ist, aber das Formular nicht gültig ist
            messages.error(request, 'Bitte prüfen Sie Ihre Eingaben zum Passwort.')

            if request.headers.get('HX-Request'):
                error_messages = list(get_messages(request))
                return HttpResponse('<div class="alert alert-danger">Bitte prüfen Sie Ihre Eingaben zum Passwort.</div>')

        # Erfolgreiches Update der Profildaten
        messages.success(request, 'Profildaten erfolgreich geändert!')

        if request.headers.get('HX-Request'):
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
            list(get_messages(request))
            return response

        return redirect('edit_profile')

    # GET-Anfrage: Rendern des Profilbearbeitungsformulars und des Passwortänderungsformulars
    password_change_form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'accounts/profile_edit_form.html', {
        'user': request.user,
        'password_change_form': password_change_form
    })


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def delete_profile(request):
    """
    Deletes the user profile and performs additional actions such as logging out the user and displaying a success
    message.

    :param request: The HTTP request object containing metadata about the request.

    Returns:
    - If the request is a HTMX request, an HttpResponse object with a success message and a redirect header to the
    homepage is returned.
    - If the request is not a HTMX request, a HttpResponseRedirect object is returned to redirect the user to the
    homepage.

    """
    if request.method == 'POST':
        # Benutzer löschen
        user = request.user
        user.delete()

        # Nutzer ausloggen
        logout(request)

        # Erfolgsmeldung
        messages.success(request, 'Profil erfolgreich gelöscht!')

        # HTMX-Anfrage: Navbar aktualisieren und auf Startseite umleiten
        if request.headers.get('HX-Request'):
            response = HttpResponse(f'''
                <div class="alert alert-success">Profil erfolgreich gelöscht!</div>

                <!-- Navbar auf den Zustand eines ausgeloggten Nutzers zurücksetzen -->
                <ul class="navbar-nav ml-auto" hx-swap-oob="true" id="user-navbar">
                    <li class="nav-item">
                        <a class="nav-link" href="{request.build_absolute_uri('/login/')}">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{request.build_absolute_uri('/register/')}">Registrieren</a>
                    </li>
                </ul>
            ''')

            # Konsumiere Nachrichten, um Duplikate zu vermeiden
            list(get_messages(request))
            response['HX-Redirect'] = '/'  # Leitet nach erfolgreicher Löschung auf die Startseite um
            return response

        # Nicht-HTMX: Erfolgsnachricht und Weiterleitung zur Startseite
        return redirect('library')

    return redirect('profile')

def login_view(request):
    """
    This method represents the login view of a web application. It is responsible for handling the login functionality.

    :param request: The HTTP request object containing metadata about the request.
    """
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
    """
    Log out the user and redirect them to the login page.

    :param request: The HTTP request object.
    :type request: HttpRequest
    """
    logout(request)
    return redirect('login')  #Wenn Logout-Button betätigt -> Abmeldung


@login_required
def update_navbar(request):
    """
    Updates the navigation bar.

    This method is triggered when the user initiates an update to the navigation bar.
    It requires the user to be logged in, as indicated by the @login_required decorator.

    :param request: The HTTP request object.

    :returns: HttpResponse: The rendered base.html template.
    """
    return render(request, 'base.html')
