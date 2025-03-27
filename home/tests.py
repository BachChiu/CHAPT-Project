from django.test import TestCase

from django.test import TestCase, Client
from django.urls import reverse
from home.models import Account, Roletable

class LoginTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup test roles and user account
        cls.client = Client()
        cls.login_url = reverse('loginView')  # Replace with the actual name in urls.py

        # Create roles
        cls.role_employee = Roletable.objects.create(userrole='Employee')
        cls.role_employer = Roletable.objects.create(userrole='Employer')

        # Create a test account (make sure the password matches whatever login view expects)
        cls.test_user = Account.objects.create(
            userid='testuser',
            firstname='Jane',
            lastname='Doe',
            userpass='testpass123'  # Store password appropriately if hashing is expected
        )

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'userid': 'testuser',
            'userpass': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)  # or 302 if it redirects
        self.assertContains(response, "Dashboard")  # Replace with something expected on success page
