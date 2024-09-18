from django.test import TestCase, Client

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from Library.models import QuizPool, QuizTask, Answer
from Multiplayer.models import MPGame, MPGame_contains_Quiztask
from Multiplayer.views import assign_tasks_to_game


class MultiplayerViewsTest(TestCase):

    def setUp(self):
        # Erstelle Testbenutzer
        self.user1 = User.objects.create_user(username='testuser1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')

        # Erstelle ein QuizPool-Objekt
        self.pool = QuizPool.objects.create(name='Test Pool')

        # Erstelle ein MPGame-Objekt
        self.game = MPGame.objects.create(pool=self.pool, player1=self.user1)

        # Erstelle einige QuizTasks für das MPGame
        self.task1 = QuizTask.objects.create(pool=self.pool, question="Test Question 1")
        self.task2 = QuizTask.objects.create(pool=self.pool, question="Test Question 2")
        MPGame_contains_Quiztask.objects.create(game=self.game, task=self.task1, current_turn=self.user1)
        MPGame_contains_Quiztask.objects.create(game=self.game, task=self.task2, current_turn=self.user1)

    def test_mp_overview(self):
        # Teste, ob die mp_overview-View richtig lädt
        self.client.login(username='testuser1', password='password')
        response = self.client.get(reverse('multiplayer:mp_overview'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multiplayer/mp_overview.html')

    def test_mp_new_game(self):
        # Teste, ob die mp_new_game-View richtig lädt
        self.client.login(username='testuser1', password='password')
        response = self.client.get(reverse('multiplayer:mp_new_game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multiplayer/mp_new_game.html')
        self.assertContains(response, 'Test Pool')

    def test_join_game_creates_new_game(self):
        # Teste, ob ein neues Spiel erstellt wird, wenn kein bestehendes Spiel vorhanden ist
        self.client.login(username='testuser1', password='password')
        response = self.client.post(reverse('multiplayer:join_game', args=[self.pool.id]))
        new_game = MPGame.objects.get(player1=self.user1)
        self.assertRedirects(response, reverse('multiplayer:mp_lobby', args=[new_game.id]))

    def test_mp_lobby_renders_correctly(self):
        # Teste, ob die Lobby korrekt gerendert wird
        self.client.login(username='testuser1', password='password')
        response = self.client.get(reverse('multiplayer:mp_lobby', args=[self.game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multiplayer/mp_lobby.html')

    def test_render_game_redirects_when_no_more_tasks(self):
        # Teste, ob bei abgeschlossenen Aufgaben zur Ergebnissseite weitergeleitet wird
        self.client.login(username='testuser1', password='password')
        self.game.completed = True
        self.game.save()
        response = self.client.get(reverse('multiplayer:render_game', args=[self.game.id]))
        self.assertRedirects(response, reverse('multiplayer:mp_game_result', args=[self.game.id]))

    def test_render_quiztask_card(self):
        # Teste, ob die Quiztask-Karte korrekt geladen wird
        self.client.login(username='testuser1', password='password')
        response = self.client.post(reverse('multiplayer:render_quiztask_card', args=[self.game.id, self.task1.id, 'select_answer']), {'selected_answer': '1'})
        self.assertEqual(response.status_code, 200)

    def test_mp_resume_game(self):
        # Teste, ob die View mp_resume_game korrekt lädt
        self.client.login(username='testuser1', password='password')
        response = self.client.get(reverse('multiplayer:mp_resume_game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multiplayer/mp_resume_game.html')

    def test_mp_game_result(self):
        # Teste, ob die View mp_game_result korrekt funktioniert
        self.client.login(username='testuser1', password='password')
        response = self.client.get(reverse('multiplayer:mp_game_result', args=[self.game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multiplayer/mp_game_result.html')

    def test_mp_lobby_content_redirect_when_game_is_full(self):
        # Teste, ob die View mp_lobby_content richtig weiterleitet, wenn das Spiel voll ist
        self.client.login(username='testuser1', password='password')
        self.game.player2 = self.user2
        self.game.save()
        response = self.client.get(reverse('multiplayer:mp_lobby_content', args=[self.game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('HX-Redirect', response.headers)

class MultiplayerIntegrationTests(TestCase):

    def setUp(self):
        # Erstelle Benutzer
        self.user1 = User.objects.create_user(username='testuser1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')

        # Erstelle QuizPool, QuizTask und Answer
        self.pool = QuizPool.objects.create(name='Test Pool', creator=self.user1)
        self.task1 = QuizTask.objects.create(pool=self.pool, question="Test Question 1", creator=self.user1)
        self.answer1 = Answer.objects.create(task=self.task1, answer="Answer 1", correct=True, explanation="Test Explanation", creator=self.user1)
        self.answer2 = Answer.objects.create(task=self.task1, answer="Answer 2", correct=False, explanation="Test Explanation", creator=self.user1)

        # Client-Authentifizierung
        self.client = Client()
        self.client.login(username='testuser1', password='password')

    def test_create_and_join_game_flow(self):
        # Benutzer 1 erstellt ein neues Spiel
        response = self.client.post(reverse('multiplayer:join_game', args=[self.pool.id]), follow=True)
        game = MPGame.objects.get(player1=self.user1)
        self.assertEqual(game.player1, self.user1)
        self.assertIsNone(game.player2)

        # Überprüfen, ob die richtige Seite nach der Weiterleitung angezeigt wird
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multiplayer/mp_lobby.html')

        # Benutzer 2 tritt bei
        self.client.logout()
        self.client.login(username='testuser2', password='password')
        response = self.client.post(reverse('multiplayer:join_game', args=[self.pool.id]), follow=True)
        game.refresh_from_db()
        self.assertEqual(game.player2, self.user2)

        # Überprüfen, ob die richtige Seite nach der Weiterleitung angezeigt wird
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multiplayer/mp_game.html')



