from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class ViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        self.sign_up_url = reverse('sign_up')
        self.delete_profile_url = reverse('delete_profile')
        self.login_htmx_url = reverse('login_htmx')
        self.register_htmx_url = reverse('register_htmx')
        self.edit_profile_url = reverse('edit_profile')
        self.logout_url = reverse('logout')
        self.profile_view_url = reverse('profile_view')

    def test_sign_up_get(self):
        response = self.client.get(self.sign_up_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/sign-up.html')

    def test_sign_up_post(self):
        response = self.client.post(self.sign_up_url, {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login after sign-up
        self.assertRedirects(response, self.login_url)

    def test_profile_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_post(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.profile_url, {
            'username': 'updateduser',
            'email': 'updatedemail@example.com',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after updating profile
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_delete_profile_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.delete_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/delete_profile.html')

    def test_delete_profile_post(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.delete_profile_url, {'confirm': True})
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='testuser')

    def test_login_htmx_post_success(self):
        response = self.client.post(self.login_htmx_url, {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Login erfolgreich!'})

    def test_login_htmx_post_failure(self):
        response = self.client.post(self.login_htmx_url, {
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'message': 'Ungültige Anmeldedaten.'})

    def test_register_htmx_post_success(self):
        response = self.client.post(self.register_htmx_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'role': 'user',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Registrierung erfolgreich!'})

    def test_register_htmx_post_password_mismatch(self):
        response = self.client.post(self.register_htmx_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'role': 'user',
            'password1': 'password1',
            'password2': 'password2'
        })
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'message': 'Passwörter stimmen nicht überein.'})

    def test_edit_profile_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.edit_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_edit_form.html')

    def test_edit_profile_post(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.edit_profile_url, {
            'username': 'newusername',
            'email': 'newemail@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Profildaten erfolgreich geändert!'})

    def test_delete_profile_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.delete_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Profil erfolgreich gelöscht!'})

    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_view_post(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)