from django.test import TestCase

from django.contrib.auth.models import User
from django.urls import reverse

class LoginTest(TestCase):
    def setUp(self):
        # Create a user for testing login
        self.username = 'testuser'
        self.password = 'securepassword123'
        User.objects.create_user(username=self.username, password=self.password)

    def test_login_success(self):
        # Attempt login with correct credentials
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })

        # Check if login redirects (default behavior)
        self.assertEqual(response.status_code, 302)

        # Check if user is authenticated
        response = self.client.get('/')
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
