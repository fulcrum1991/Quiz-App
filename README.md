# IU-Quiz
Code-Repo für das Quiz-Projekt

## Strukturbeschreibung

Views
Model
Template

### wichtige Ordner und Dateien
- manage.py
  - Gateway zu Django Management Befehlen.
  - Initiiert den development server, erstellt Applikationen, startet Migrationen, etc. 
- Quiz-App/settings.py
  - Enthält die Konfiguration des Projekts wie Datenbankanbindungen.
  - "Blaupause"
- Quiz-App/urls.py
  - Navigation
  - Verbindet URLs mit den Views 
- Quiz-App/wsgi.py
  - Web Server Gateway Interface
  - Verbindet die Applikation mit dem Webserver
- Quiz-App/asgi.py
  - Asynchronous Server Gateway Interface
  - Verbindet die Applikation mit dem asyncrhonen Webserver
- Quiz-App/__init__.py
  - Organisiert und Importiert Module im Projekt
 
- Quiz-App/app/models.py
  - Definiert die Datenmodelle unter Anwendung von ORM.
  - Jede Klasse entspricht einer Tabelle in der Datenbank.
- Quiz-App/app/views.py
  - Logik der Applikation.
  - Definiert wie auf Requests reagiert wird.
- Quiz-App/app/tests.py
  - Ggf. für Unit-Tests
 - Quiz-App/app/admin.py
   - Definiert das Admin-Interface
- Quiz-App/app/migrations.py
  - Blaupasue für Ändeurngen des Models   

## Branching Strategie
![image](https://github.com/fulcrum1991/IU-Quiz/assets/96475736/88fa176a-0c88-4c22-a576-503ae47a9992)

Haupt-Branches:
- Main Branch (main):
  - Enthält den stabilen Code für die Produktion.
  - Direkte Operationen sind nicht erlaubt.
  - Änderungen müssen mit Versionsnummern getaggt werden.
- Develop Branch (develop):
  - Entwicklungsumgebung.
  - Enthält den aktuellen Stand der Entwicklung.
  - Brnaches von neuen Features werden hier erstellt und wieder zusammengeführt.

Feature-Branches:
- Branches der develop-Branch
- Arbeiten am Feature und regelmäßiges Committen
- Mergen des Feature-Branches zurück in develop
