from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .forms import SignUpForm, CustomPasswordChangeForm, UserUpdateForm, DeleteUserForm



class ViewsTestCase(TestCase):

    def setUp(self):
        # Initialisiere den Client und erstelle einen Benutzer für Tests
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.user.save()
        self.client.login(username='testuser', password='password123')

    def test_sign_up_view(self):
        # Test für die Sign-Up-Ansicht
        response = self.client.get(reverse('sign_up'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/sign-up.html')

        data = {
            'username': 'newuser',
            'password1': 'mypassword123',
            'password2': 'mypassword123'
        }
        response = self.client.post(reverse('sign_up'), data)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('library'))

    def test_profile_view(self):
        # Test für die Profil-Ansicht
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_update_post(self):
        # Test für die Profilaktualisierung (POST)
        data = {
            'username': 'updateduser',
            'email': 'newemail@test.com',
            'old_password': 'password123',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        response = self.client.post(reverse('profile'), data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertNotEquals(self.user.username, 'updateduser')
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_delete_profile_view(self):
        # Test für das Löschen des Profils
        response = self.client.get(reverse('delete-profile'))
        self.assertEqual(response.status_code, 405)
        self.assertTemplateUsed(response, 'accounts/delete_profile.html')

        data = {'confirm': True}
        response = self.client.post(reverse('delete_profile'), data)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_login_htmx(self):
        # Test für HTMX-Login
        data = {
            'username': 'testuser',
            'password': 'password123',
        }
        response = self.client.post(reverse('login-htmx'), data)
        self.assertEqual(response.status_code, 200)

    def test_register_htmx(self):
        # Test für HTMX-Registrierung
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123'
        }
        response = self.client.post(reverse('register-htmx'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_edit_profile(self):
        # Test für das Bearbeiten des Profils
        data = {
            'username': 'editeduser',
            'email': 'editedemail@test.com',
            'old_password': 'password123',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123',
        }
        response = self.client.post(reverse('edit-profile'), data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'editeduser')

    def test_logout_view(self):
        # Test für die Logout-Ansicht
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)
        self.assertRedirects(response, reverse('login'))


