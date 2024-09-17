from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import QuizPool, QuizTask, Answer
from .forms import QuizPoolForm, QuizTaskForm, AnswerForm

class LibraryViewTests(TestCase):

    def setUp(self):
        # Setup Testdaten
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.quizpool = QuizPool.objects.create(name="Test Pool", creator=self.user)
        self.quiztask = QuizTask.objects.create(question="Test Task", pool=self.quizpool, creator=self.user)
        self.answer = Answer.objects.create(answer="Test Answer", task=self.quiztask, creator=self.user)

    def test_get_library_content(self):
        # Testet die Funktion get_library_content
        response = self.client.get(reverse('library'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('quizpools', response.context)
        self.assertIn('quiztasks', response.context)
        self.assertIn('selected_pool', response.context)
        self.assertIn('selected_task', response.context)

    def test_create_quizpool(self):
        # Testet die Erstellung eines neuen Quizpools
        form_data = {'name': 'New Quiz Pool'}
        response = self.client.post(reverse('create_quizpool'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(QuizPool.objects.filter(name='New Quiz Pool').exists())

    def test_change_quizpool_name(self):
        # Testet das Ändern des Namens eines Quizpools
        form_data = {'name': 'Updated Pool Name'}
        response = self.client.post(reverse('change_quizpool_name', args=[self.quizpool.id]), form_data)
        self.quizpool.refresh_from_db()
        self.assertEqual(self.quizpool.name, 'Updated Pool Name')

    def test_delete_quizpool(self):
        # Testet das Löschen eines Quizpools
        response = self.client.post(reverse('delete_quizpool', args=[self.quizpool.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(QuizPool.objects.filter(id=self.quizpool.id).exists())

    def test_create_quiztask(self):
        # Testet die Erstellung eines neuen Quiztasks
        form_data = {'question': 'New Quiz Task'}
        response = self.client.post(reverse('create_quiztask', args=[self.quizpool.id]), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(QuizTask.objects.filter(question='New Quiz Task').exists())

    def test_change_question(self):
        # Testet das Ändern der Frage eines Quiztasks
        form_data = {'question': 'Updated Question'}
        response = self.client.post(reverse('change_question', args=[self.quiztask.id]), form_data)
        self.quiztask.refresh_from_db()
        self.assertEqual(self.quiztask.question, 'Updated Question')

    def test_delete_quiztask(self):
        # Testet das Löschen eines Quiztasks
        response = self.client.post(reverse('delete_quiztask', args=[self.quiztask.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(QuizTask.objects.filter(id=self.quiztask.id).exists())

    def test_create_answer(self):
        # Testet die Erstellung einer neuen Answer
        form_data = {'answer': 'New Answer', 'correct': 'False'}
        response = self.client.post(reverse('create_answer', args=[self.quiztask.id]), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Answer.objects.filter(answer='New Answer').exists())

    def test_edit_answer(self):
        # Testet das Bearbeiten einer Answer
        form_data = {'answer': 'Updated Answer', 'explanation': 'Explanation', 'correct': 'True'}
        response = self.client.post(reverse('edit_answer', args=[self.answer.id]), form_data)
        self.answer.refresh_from_db()
        self.assertEqual(self.answer.answer, 'Updated Answer')
        self.assertEqual(self.answer.correct, True)

    def test_delete_answer(self):
        # Testet das Löschen einer Answer
        response = self.client.post(reverse('delete_answer', args=[self.answer.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Answer.objects.filter(id=self.answer.id).exists())
