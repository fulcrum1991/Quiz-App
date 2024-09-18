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


class IntegrationTests(TestCase):

    def setUp(self):
        # Set up Testdaten
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.quizpool = QuizPool.objects.create(name="Test Pool", creator=self.user)
        self.quiztask = QuizTask.objects.create(question="Test Task", pool=self.quizpool, creator=self.user)
        self.answer = Answer.objects.create(answer="Test Answer", task=self.quiztask, creator=self.user)

    def test_create_quizpool_and_create_quiztask(self):
        # Integrationstest für die Erstellung eines Quizpools und einer Quizaufgabe
        pool_data = {'name': 'Integrated Quiz Pool'}
        response = self.client.post(reverse('create_quizpool'), pool_data)
        self.assertEqual(response.status_code, 200)
        created_pool = QuizPool.objects.get(name='Integrated Quiz Pool')

        task_data = {'question': 'Integrated Quiz Task'}
        response = self.client.post(reverse('create_quiztask', args=[created_pool.id]), task_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(QuizTask.objects.filter(question='Integrated Quiz Task', pool=created_pool).exists())

    def test_create_quizpool_quiztask_and_answer(self):
        # Integrationstest für die Erstellung eines Quizpools, einer Quizaufgabe und einer Antwort
        pool_data = {'name': 'Integrated Pool'}
        response = self.client.post(reverse('create_quizpool'), pool_data)
        self.assertEqual(response.status_code, 200)
        created_pool = QuizPool.objects.get(name='Integrated Pool')

        task_data = {'question': 'Integrated Task'}
        response = self.client.post(reverse('create_quiztask', args=[created_pool.id]), task_data)
        self.assertEqual(response.status_code, 200)
        created_task = QuizTask.objects.get(question='Integrated Task', pool=created_pool)

        answer_data = {'answer': 'Integrated Answer', 'correct': 'False'}
        response = self.client.post(reverse('create_answer', args=[created_task.id]), answer_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Answer.objects.filter(answer='Integrated Answer', task=created_task).exists())

    def test_quizpool_task_and_answer_deletion(self):
        # Integrationstest für das Löschen eines Quizpools, einer Aufgabe und einer Antwort
        response = self.client.post(reverse('delete_answer', args=[self.answer.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Answer.objects.filter(id=self.answer.id).exists())

        response = self.client.post(reverse('delete_quiztask', args=[self.quiztask.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(QuizTask.objects.filter(id=self.quiztask.id).exists())

        response = self.client.post(reverse('delete_quizpool', args=[self.quizpool.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(QuizPool.objects.filter(id=self.quizpool.id).exists())

    def test_quiztask_with_multiple_answers(self):
        # Integrationstest für eine Quizaufgabe mit mehreren Antworten
        answer_data1 = {'answer': 'Answer 1', 'correct': 'True'}
        answer_data2 = {'answer': 'Answer 2', 'correct': 'False'}

        self.client.post(reverse('create_answer', args=[self.quiztask.id]), answer_data1)
        self.client.post(reverse('create_answer', args=[self.quiztask.id]), answer_data2)

        task_answers = Answer.objects.filter(task=self.quiztask)
        self.assertEqual(task_answers.count(), 3)  # 1 bestehende Antwort plus 2 neue

        # Überprüfen, ob die Antworten korrekt gespeichert wurden
        self.assertTrue(Answer.objects.filter(answer='Answer 1', correct=True).exists())
        self.assertTrue(Answer.objects.filter(answer='Answer 2', correct=False).exists())