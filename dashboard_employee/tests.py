from django.test import TestCase, Client
from django.urls import reverse

class EmployeeDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_employee_dashboard_view(self):
        response = self.client.get(reverse('employeeView'))  # from urls.py
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_employee/employee_dashboard.html')
