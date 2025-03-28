from django.test import TestCase, Client
from django.urls import reverse

class EmployerDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_employer_dashboard_view(self):
        response = self.client.get(reverse('employerView'))  # from urls.py
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_employer/employer_dashboard.html')
