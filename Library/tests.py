from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from Library.models import QuizPool, QuizTask, Answer
from Singleplayer.models import SPGame, SPGame_contains_Quiztask
import datetime as dt


class SingleplayerViewsTestCase(TestCase):

    def setUp(self):
        # Erstelle Testdaten für User, QuizPool, QuizTask, usw.
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        self.quizpool = QuizPool.objects.create(name="Test Pool", creator=self.user)
        self.quiztask = QuizTask.objects.create(question="Test Question", pool=self.quizpool)
        self.answer = Answer.objects.create(answer="Test Answer", correct=True, task=self.quiztask)

        self.sp_game = SPGame.objects.create(name="Test Game", user=self.user, pool=self.quizpool)
        self.sp_game_quiztask = SPGame_contains_Quiztask.objects.create(game=self.sp_game, task=self.quiztask)

    def test_sp_overview_view(self):
        response = self.client.get(reverse('sp_overview'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_overview.html')

    def test_sp_new_game_view(self):
        response = self.client.get(reverse('sp_new_game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_new_game.html')
        self.assertIn('quizpools', response.context)

    def test_show_lib_content_view(self):
        response = self.client.get(reverse('show_lib_content', args=[self.quizpool.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_new_game_content.html')
        self.assertEqual(response.context['selected_pool'], self.quizpool)

    def test_create_game_view(self):
        response = self.client.post(reverse('create_game', args=[self.quizpool.id]))
        self.assertRedirects(response, reverse('render_game', args=[SPGame.objects.last().id]))
        self.assertTrue(SPGame_contains_Quiztask.objects.filter(game=SPGame.objects.last()).exists())

    def test_render_game_view(self):
        response = self.client.get(reverse('render_game', args=[self.sp_game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_game.html')
        self.assertIn('sp_game', response.context)

    def test_render_quiztask_card_view(self):
        response = self.client.get(reverse('render_quiztask_card', args=[self.sp_game.id, self.quiztask.id, 'next']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/quiztask_card.html')

    def test_evaluate_task_view(self):
        response = self.client.post(reverse('evaluate_task', args=[self.sp_game.id, self.quiztask.id, self.answer.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/quiztask_card.html')
        sp_game_quiztask = SPGame_contains_Quiztask.objects.get(game=self.sp_game, task=self.quiztask)
        self.assertTrue(sp_game_quiztask.correct_answered)

    def test_render_game_result_card_view(self):
        self.sp_game.correct_percent = 100
        self.sp_game.save()
        response = self.client.get(reverse('render_game_result_card', args=[self.sp_game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/game_result_card.html')
        self.assertEqual(response.context['sp_game'], self.sp_game)

    def test_sp_resume_game_view(self):
        response = self.client.get(reverse('sp_resume_game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_resume_game.html')

    def test_sp_history_view(self):
        self.sp_game.completed = True
        self.sp_game.save()
        response = self.client.get(reverse('sp_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'singleplayer/sp_history.html')