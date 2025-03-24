
'''from django.test import TestCase, Client
from django.urls import reverse
from common.models import Account, Company, Employed, Roletable
from django.contrib.auth.hashers import check_password

class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')  # Ensure the correct URL name
        self.company = Company.objects.create(companyid='12345')
        self.role_employee = Roletable.objects.create(userrole='Employee')
        self.role_employer = Roletable.objects.create(userrole='Employer')
        
    def test_registration_missing_fields(self):
        response = self.client.post(self.url, {})
        self.assertContains(response, "Username is required.")
    
    def test_registration_existing_user(self):
        Account.objects.create(userid='existing_user', firstname='John', lastname='Doe', userpass='hashedpassword')
        response = self.client.post(self.url, {
            'userID': 'existing_user',
            'fname': 'John',
            'lname': 'Doe',
            'userPass': 'password123',
            'userPass2': 'password123',
            'companyID': self.company.companyid,
            'role': 'Employee'
        })
        self.assertContains(response, "User already exists. Try another userID.")
    
    def test_registration_password_mismatch(self):
        response = self.client.post(self.url, {
            'userID': 'newuser',
            'fname': 'Jane',
            'lname': 'Doe',
            'userPass': 'password123',
            'userPass2': 'password456',
            'companyID': self.company.companyid,
            'role': 'Employee'
        })
        self.assertContains(response, "Passwords do not match.")

    def test_registration_password_too_short(self):
        response = self.client.post(self.url, {
            'userID': 'newuser',
            'fname': 'Jane',
            'lname': 'Doe',
            'userPass': 'short',
            'userPass2': 'short',
            'companyID': self.company.companyid,
            'role': 'Employee'
        })
        self.assertContains(response, "Password must be at least 8 characters long.")
    
    def test_successful_employee_registration(self):
        response = self.client.post(self.url, {
            'userID': 'newemployee',
            'fname': 'Alice',
            'lname': 'Smith',
            'userPass': 'securepassword',
            'userPass2': 'securepassword',
            'companyID': self.company.companyid,
            'role': 'Employee'
        })
        self.assertContains(response, "Employee created")
        user = Account.objects.get(userid='newemployee')
        self.assertTrue(check_password('securepassword', user.userpass))
    
    def test_successful_employer_registration(self):
        response = self.client.post(self.url, {
            'userID': 'newemployer',
            'fname': 'Bob',
            'lname': 'Brown',
            'userPass': 'securepassword',
            'userPass2': 'securepassword',
            'companyID': self.company.companyid,
            'role': 'Employer'
        })
        self.assertContains(response, "Employer created")
        user = Account.objects.get(userid='newemployer')
        self.assertTrue(check_password('securepassword', user.userpass))
        self.assertTrue(Company.objects.filter(employerid=user).exists())'''

