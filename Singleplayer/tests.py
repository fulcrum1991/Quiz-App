from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from Library.models import QuizPool, QuizTask, Answer
from Singleplayer.models import SPGame, SPGame_contains_Quiztask
import datetime as dt

class SingleplayerViewsTests(TestCase):

    def setUp(self):
        # Create a user and log in
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        # Create a QuizPool for testing
        self.quizpool = QuizPool.objects.create(name="Test Quiz Pool")

        # Create some QuizTasks for the pool
        self.quiztask1 = QuizTask.objects.create(name="Task 1", pool=self.quizpool)
        self.quiztask2 = QuizTask.objects.create(name="Task 2", pool=self.quizpool)

    def test_sp_overview_view(self):
        response = self.client.get(reverse('sp_overview'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_overview.html')

    def test_sp_new_game_view(self):
        response = self.client.get(reverse('sp_new_game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_new_game.html')
        self.assertIn('quiztasks', response.context)  # Ensure library content is passed to context

    def test_show_lib_content_view(self):
        response = self.client.get(reverse('show_lib_content', kwargs={'pool_id': self.quizpool.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_new_game_content.html')
        self.assertIn('quiztasks', response.context)

    def test_create_game_view(self):
        response = self.client.post(reverse('create_game', kwargs={'pool_id': self.quizpool.id}))
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertTrue(SPGame.objects.filter(user=self.user, pool=self.quizpool).exists())

    def test_render_game_view(self):
        # Create a test game for this view
        sp_game = SPGame.objects.create(name="Test Game", user=self.user, pool=self.quizpool)
        response = self.client.get(reverse('render_game', kwargs={'game_id': sp_game.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_game.html')
        self.assertIn('questions_list', response.context)

    def test_render_quiztask_card_view(self):
        # Create a game and associated quiz tasks
        sp_game = SPGame.objects.create(name="Test Game", user=self.user, pool=self.quizpool)
        sp_game_quiztask = SPGame_contains_Quiztask.objects.create(game=sp_game, task=self.quiztask1)

        response = self.client.get(reverse('render_quiztask_card', kwargs={'game_id': sp_game.id, 'task_id': self.quiztask1.id, 'action': 'next'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/quiztask_card.html')

    def test_evaluate_task_view(self):
        # Create a game and associated quiz tasks
        sp_game = SPGame.objects.create(name="Test Game", user=self.user, pool=self.quizpool)
        sp_game_quiztask = SPGame_contains_Quiztask.objects.create(game=sp_game, task=self.quiztask1)
        correct_answer = Answer.objects.create(task=self.quiztask1, text="Correct Answer", correct=True)

        response = self.client.post(reverse('evaluate_task', kwargs={'game_id': sp_game.id, 'task_id': self.quiztask1.id, 'selected_answer_id': correct_answer.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/quiztask_card.html')

    def test_render_game_result_card_view(self):
        sp_game = SPGame.objects.create(name="Test Game", user=self.user, pool=self.quizpool)
        response = self.client.get(reverse('render_game_result_card', kwargs={'game_id': sp_game.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/game_result_card.html')

    def test_sp_resume_game_view(self):
        # Create an unfinished game
        unfinished_game = SPGame.objects.create(name="Unfinished Game", user=self.user, pool=self.quizpool)
        response = self.client.get(reverse('sp_resume_game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_resume_game.html')
        self.assertIn('unfinished_games', response.context)
        self.assertTrue(unfinished_game in response.context['unfinished_games'])

    def test_sp_history_view(self):
        # Create a finished game
        finished_game = SPGame.objects.create(name="Finished Game", user=self.user, pool=self.quizpool, completed=True)
        response = self.client.get(reverse('sp_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_history.html')
        self.assertIn('finished_games', response.context)
        self.assertTrue(finished_game in response.context['finished_games'])

