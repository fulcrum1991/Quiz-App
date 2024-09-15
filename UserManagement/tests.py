from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import auth

class UserManagementTests(TestCase):
    def setUp(self):
        # Erstelle einen Testnutzer
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com'
        )
        self.client = Client()

    def test_signup_view(self):
        # Test für die Registrierung (GET)
        response = self.client.get(reverse('sign_up'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/sign-up.html')

        # Test für die Registrierung (POST)
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newuserpassword',
            'password2': 'newuserpassword'
        }
        response = self.client.post(reverse('sign_up'), data)
        self.assertEqual(response.status_code, 302)  # Weiterleitung auf 'login'
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_profile_view_logged_in(self):
        # Test für die Profilansicht eines eingelogten Nutzers
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_view_not_logged_in(self):
        # Test für die Profilansicht eines nicht eingelogten Nutzers
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Weiterleitung auf 'login'

    def test_delete_profile(self):
        # Test für das Löschen des Profils
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('delete_profile'), {'confirm': True})
        self.assertEqual(response.status_code, 302)  # Weiterleitung auf 'home'
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_login_htmx(self):
        # Test für den HTMX-Login
        response = self.client.post(reverse('login_htmx'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login erfolgreich', response.content)

    def test_register_htmx(self):
        # Test für den HTMX-Registerprozess
        data = {
            'username': 'htmxuser',
            'email': 'htmxuser@example.com',
            'password1': 'htmxpassword',
            'password2': 'htmxpassword'
        }
        response = self.client.post(reverse('register_htmx'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registrierung erfolgreich', response.content)
        self.assertTrue(User.objects.filter(username='htmxuser').exists())

    def test_edit_profile(self):
        # Test für das Bearbeiten des Profils
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('edit_profile'), {
            'username': 'updateduser',
            'email': 'updateduser@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Weiterleitung nach 'edit_profile'
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.username, 'updateduser')
        self.assertEqual(user.email, 'updateduser@example.com')

    def test_login_view(self):
        # Test für die Login-Ansicht
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(auth.get_user(self.client).username, 'testuser')

    def test_logout_view(self):
        # Test für die Logout-Ansicht
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Weiterleitung nach 'login'
        self.assertFalse(auth.get_user(self.client).is_authenticated)
