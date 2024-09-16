
# README
## Quiz-App
- [Logo]

Willkommen zum Quiz-App-Projekt im Kurs ISEF der IU.
Dieses Dokument gibt einen Überblick über die Dokumentation des  Produkts und dessen Entwicklung.

**App und Teaminformation**
App Name : Quiz-App
Auftraggeber : IU  
Development Team :   
- Mario Kaiser
- Marvin Schilling
- Benjamin Werner
- Andreas Otto
- Benjamin Orbon (Pütz)
Web URL : https://quiz-app-f4ajb6d9hydqdgf8.germanywestcentral-01.azurewebsites.net/

**Entwicklungsumgebung:**
- Windows 11 Evalation als VM
- Pycharm
- mit Python 3.12 Interpreter
- Django Framework
- SQLite als lokale Datenbank

**Bereitstellungsumgebung:**  
- Microsoft Azure App Services

**Frameworks und Bibliotheken**
- Django 5.0.7
- python-dotenv 1.0.1
- whitenoise 6.6.0
- django-redis 5.4.0
- crispy-bootstrap5
- gunicorn 20.1.0
- psycopg2-binary 2.9.9
- htmx 2.0.0

**Beschreibung der Projektentwicklung**
Das Projekt IU-Quiz ist eine Quiz-Anwendung, die in Django, ein leistungsfähiges Python-Framework für webbasierte Anwendungen, implementiert ist.
Im Projekt sind die Datenmodelle, die logischen Ansichten und die HTML-Vorlagen in separaten Modulen gespeichert, die der Django-eigenen Model-View-Template (MVT) Architektur entsprechen. 
Die Anwendung nutzt zudem HTMX - eine moderne HTML-basierte Technologie, die es ermöglicht, AJAX-Aufrufe, CSS Transitionen, WebSockets und Server Sent Events direkt im HTML-Markup zu handhaben.
Das Projekt verwendet auch eine sorgfältige Branching-Strategie für die Versionskontrolle:
Der main-Branch enthält den stabilen Code für die Produktion.
Der develop-Branch ist die aktive Entwicklungsumgebung. Hier werden neue Feature-Branches erstellt und wieder zusammengeführt.
Das Projekt ist mittels eines Web Server Gateway Interface (wsgi.py) mit einem Webserver verknüpft. Konfigurationsdetails sind in der Datei settings.py enthalten und URL-Routing wird in urls.py geregelt. 


### Branching Strategie
Das Projekt verwendet eine sorgfältige Branching-Strategie für die Versionskontrolle:

Haupt-Branches:
- Main Branch (main):
	- Enthält den stabilen Code für die Produktion.
	- Direkte Operationen sind nicht erlaubt.
	- Änderungen müssen mit Versionsnummern getaggt werden.
- Development Branch (development):
	- Entwicklungsumgebung.
	- Enthält den aktuellen Stand der Entwicklung.
	- Hier werden neue Feature-Branches erstellt und wieder zusammengeführt.
- Feature-Branches:
	- Branches der development-Branch
	- Arbeiten am Feature und regelmäßiges Committen
	- Mergen des Feature-Branches zurück in development

----
## Strukturbeschreibung

Das Django-Projekt gliedert sich in die folgenden Apps:
- Quiz-App
- UserManagement
- Library
- Singleplayer
- Multiplayer

Nachfolgend sind die wichtigsten Datei des Projekts beschrieben.


HTML-Vorlagen, die in Django zum Erzeugen von HTML-Antworten verwendet werden, befinden sich im templates-Verzeichnis.

#### wichtige wiederkehrende Dateien
Diese Dateien sind u.a. Bestandteil jeder App
- models.py
	- In models.py sind die Datenmodelle definiert. Diese Modelle verwenden das Django ORM (Object-Relational Mapping) und jede Klasse in models.py entspricht einer Tabelle in der Datenbank.
	- **Dazugehöriges ERM**
		- ERM.drawio.pdf
		- Erläutung_zum_ERM-docx
- views.py
	- Die views.py definiert die Geschäftslogik und enthält Funktionen, die HTTP-Anfragen behandeln und HTTP-Antworten zurückgeben.
- templates
	- HTML-Vorlagen, die in Django zum Erzeugen von HTML-Antworten verwendet werden, befinden sich im templates-Verzeichnis.
### Apps
#### Quiz-App
Diese App managed die gesamte Applikation

- Quiz-App/settings.py
	- Die settings.py Datei ist die Konfigurationsdatei für eine Django-Webanwendung. Sie definiert grundlegende Einstellungen wie geheime Schlüssel (SECRET_KEY), Debug-Zustand (DEBUG), erlaubte Hosts (ALLOWED_HOSTS), ietc.

- Quiz-App/production.py
	- Die production.py ist eine spezielle Konfigurationsdatei für eine Django-Webanwendung, die auf Azure gehostet wird. Sie importiert die Basiseinstellungen aus der settings.py und modifiziert einige davon für die Produktion in Azure. 

- Quiz-App/wsgi.py
	- Die wsgi.py Datei ist die Eintrittspunkt für WSGI-kompatible Webserver zur Bedienung der Django-Anwendung. Sie definiert eine application Variable, die das WSGI-Application-Object der Django-Anwendung referenziert. Anhängig davon, ob die Anwendung auf Azure gehostet wird oder nicht (basierend auf der Prüfung der WEBSITE_HOSTNAME Umgebungsvariable), wird das Einstellungsmodul auf Quiz-App.production oder Quiz-App.settings gesetzt.

- Quiz-App/urls.py
	- Die urls.py Datei definiert die URL-Konfiguration der Django-Anwendung. Es werden Routen (/URL Muster) zu den entsprechenden Views (Funktionen oder Klassen, die HTTP-Anfragen bearbeiten) definiert.


#### UserManagement
Diese App behandelt alles rund um das Management von Benutzerprofilen. Dazu gehören u.a.:
	- Rollen/Rechte-Management
	- Authentifizierung

- UserManagement/views.py
	- In dieser views.py gibt es Funktionen für die Nutzerverwaltung wie Registrierung (sign_up, register_htmx), Profilverwaltung (profile, delete_profile, profile_view, edit_profile), Login (login_htmx, login_view), Logout (logout_view) und Aktualisierung der Navigationsleiste (update_navbar).

**Dazugehörige Wireframes**
- Login
- Registrieren
- Profil
**Dazugehörige Flowcharts**
- UF1 - Einlogen oder Registrieren
- UF7 - Profildaten anzeigen & ändern

#### Library
Diese App behandelt das Darstellen und Managen von Aufgaben für das Quiz. U.a.:
- Verwalten von Quizpools
- Verwalten von Fragen
- Verwalten von Antworten

- Library/views.py
	- In dieser views.py gibt es Funktionen für die Verwaltung von Quizfragen und die Antworten darauf, einschließlich Abrufen von Bibliothekscontent (get_library_content), Anzeigen einer Bibliothek (show_library), Erstellen/Löschen/Bearbeiten von Quizpools und Quiz-Aufgaben (create_quizpool, delete_quizpool, change_quizpool_name, create_quiztask, delete_quiztask, change_question), und Verwalten von Antworten zu den Quizfragen (get_answers, show_answers, create_answer, edit_answer, delete_answer).
- Library/models.py
	- In dieser models.py sind folgende Modelle definiert:
		- QuizPool: verwendet, um eine Sammlung von Quizfragen zu speichern.
		- QuizTask: verwendet, um einzelne Quizfragen zu speichern.
		- Answer: verwendet, um Antworten zu Quizfragen zu speichern.

**Dazugehörige Wireframes**
- Bibliothek
**Dazugehörige Flowcharts**
- UF2 - Bibliothek (loged out)
- UF3 - Bibliothek ansehen
- UF4 - Fragenpool erstellen / Name ändern / löschen
- UF5 - Fragen erstellen / Namen ändern / löschen
- UF6 - Antwortoptionen erstellen / ändern / löschen

#### Singleplayer
Diese App behandelt das Darstellen und Managen von Quiz' im Einzelspielermodus. U.a.:
- Neue Spiele starten
- Begonnene Spiele Fortsetzen
- Anzeigen der Ergebnisse beendeter Spiele

- Singleplayer/views.py
	- Die views.py-Datei enthält Funktionen zur Behandlung von SingleplayerSpielanfragen. Sie enthält Funktionen zur Überblicksanzeige des Spiels (sp_overview), zur Erstellung eines neuen Spiels (sp_new_game, create_game), zur Verarbeitung des Spiels und der Quizkarten (render_game, render_quiztask_card, evaluate_task, render_game_result_card), zur Fortsetzung von Spielen (sp_resume_game), und zum Anzeigen von Spielinhalten und -verlauf (show_lib_content, show_game_content, sp_history).
- Singleplayer/SPHelperFunctions.py
	- Diese Datei bietet unterstützende Funktionen für die views.py. Diese Funktionen helfen beim Erstellen, Anzeigen, Bewerten und Fortsetzen von Spielen. 
- Singleplayermodels.py
	- In dieser models.oy sind folgende Modelle definiert:
		- SPGame: wird verwendet, um einzelne Spielinstanzen zu speichern.
		- SPGame_contains_Quiztask: wird verwendet, um eine Beziehung zwischen SPGame und QuizTask zu definieren - also welche Fragen wurden in welchem Spiel gestellt.

**Dazugehörige Wireframes**
- Singleplayer
- Singleplayer - Neues Spiel
- Singleplayer - Spiel 1
- Singleplayer - Spiel 2
- Singleplayer - Ergebnis
- Singleplayer- Spiel fortsetzen
- Singleplayer- Historie
**Dazugehörige Flowcharts**
- UF7 - Einzelspieler - Aktion wählen
- UF8 - Einzelspieler - Spiel starten
- UF9 - Einzelspieler - Spielen
- UF10 - Einzelspieler - Spiel fortsetzen
- UF11 - Einzelspieler - Historie anzeigen

#### Multiplayer
Diese App behandelt das Darstellen und Managen von Quiz' im Mehrspielermodus. U.a.:
- Neue Spiele starten
- Begonnene Spiele Fortsetzen
- Anzeigen der Ergebnisse beendeter Spiele

- Multiplayer/views.py
	- Die views.py-Datei enthält Funktionen zur Behandlung von Multiplayer-Spielanfragen. Sie enthält Funktionen zur Überblicksanzeige des Spiels (mp_overview), zur Erstellung eines neuen Spiels (mp_new_game, create_game), zur Verarbeitung des Spiels und der Quizkarten (render_game, render_quiztask_card, evaluate_task, render_game_result_card), zur Fortsetzung von Spielen (mp_resume_game), und zum Anzeigen von Spielinhalten und -verlauf (show_lib_content, show_game_content, mp_history).
- Multiplayer/MPHelperFunctions.py
	- Diese Datei bietet unterstützende Funktionen für die views.py. Diese Funktionen helfen beim Erstellen, Anzeigen, Bewerten und Fortsetzen von Spielen. 
- Multiplayermodels.py
	- In dieser models.oy sind folgende Modelle definiert:
		- MPGame: wird verwendet, um einzelne Spielinstanzen zu speichern.
		- MPGame_contains_Quiztask: wird verwendet, um eine Beziehung zwischen MPGame und QuizTask zu definieren - also welche Fragen wurden in welchem Spiel gestellt.





### Templates
Der Template-Ordner in Django-Projekten wird verwendet, um HTML-Vorlagen zu speichern, die das Layout und Design der Website definieren. In diesem Projekt enthält der Template-Ordner  Vorlagen für folgende Anteile:
- Usermanagement (in den Ordnern accounts und registration)
- Library
- Singleplayer
- base.html - dient als Grundlage für das Design der Quiz-App und wird von allen templates genutzt

Diese HTML-Dateien arbeiten sowohl mit Django-Template-Funktionen, sowie HTMX, die das dynamische Erstellen von HTML-Inhalten durch Einbinden von Django-Variablen und -Funktionen ermöglichen.






 



