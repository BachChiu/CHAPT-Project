
from django.test import TestCase, Client
from django.urls import reverse
from common.models import Account, Company, Employed, Roletable
from django.contrib.auth.hashers import check_password
from django.db import connection

class RegisterViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE Account (
                userID varchar(100) NOT NULL,
                firstName varchar(100) NOT NULL,
                lastName varchar(100) NOT NULL,
                userPass varchar(256) NOT NULL,
                PRIMARY KEY (userID),
                INDEX idx_fName (firstName),
                INDEX idx_lName (lastName)
            ) ENGINE = InnoDB;
        """)

        # Create Company table
        cursor.execute("""
            CREATE TABLE Company (
                employerID varchar(100) NOT NULL,
                companyID varchar(100) NOT NULL UNIQUE,
                FOREIGN KEY (employerID) REFERENCES Account(userID),
                CONSTRAINT companyPK PRIMARY KEY (employerID, companyID)
            ) ENGINE = InnoDB;
        """)

        # Create RoleTable table
        cursor.execute("""
            CREATE TABLE RoleTable (
                userRole varchar(100),
                PRIMARY KEY (userRole)
            ) ENGINE = InnoDB;
        """)

        # Create Employed table
        cursor.execute("""
            CREATE TABLE Employed (
                employeeID varchar(100) NOT NULL,
                companyID varchar(100) NOT NULL,
                userRole varchar(100),
                userSalary decimal(19,4),
                FOREIGN KEY (employeeID) REFERENCES Account(userID),
                FOREIGN KEY (companyID) REFERENCES Company(companyID),
                FOREIGN KEY (userRole) REFERENCES RoleTable(userRole),
                CONSTRAINT employedPK PRIMARY KEY (employeeID, companyID)
            ) ENGINE = InnoDB;
        """)

        # Create Schedules table
        cursor.execute("""
            CREATE TABLE Schedules (
                scheduleID int NOT NULL AUTO_INCREMENT,
                employeeID varchar(100) NOT NULL,
                startTime datetime DEFAULT NULL,
                endTime datetime DEFAULT NULL,
                FOREIGN KEY (employeeID) REFERENCES Account(userID),
                PRIMARY KEY (scheduleID),
                INDEX idx_employee (employeeID)
            ) ENGINE = InnoDB;
        """)

        # Create Expenses table
        cursor.execute("""
            CREATE TABLE Expenses (
                employerID varchar(100) NOT NULL,
                expenseDate DATE,
                expense decimal(19,4),
                FOREIGN KEY (employerID) REFERENCES Account(userID),
                CONSTRAINT expensesPK PRIMARY KEY (employerID, expenseDate)
            ) ENGINE = InnoDB;
        """)

        # Create ShiftTime table
        cursor.execute("""
            CREATE TABLE ShiftTime (
                shiftID int NOT NULL AUTO_INCREMENT,
                employeeID varchar(100) NOT NULL,
                clockIn datetime DEFAULT NULL,
                clockOut datetime DEFAULT NULL,
                breakDuration time DEFAULT 0,
                FOREIGN KEY (employeeID) REFERENCES Account(userID),
                PRIMARY KEY(shiftID),
                INDEX idx_employee (employeeID)
            ) ENGINE = InnoDB;
        """)

        # Create Compensation table
        cursor.execute("""
            CREATE TABLE Compensation (
                shiftID int NOT NULL,
                employeeID varchar(100) NOT NULL,
                shiftCompensation decimal(19,4),
                FOREIGN KEY (shiftID) REFERENCES ShiftTime(shiftID),
                FOREIGN KEY (employeeID) REFERENCES Account(userID),
                PRIMARY KEY (shiftID),
                INDEX idx_employee (employeeID)
            ) ENGINE = InnoDB;
        """)

        # Create Break table
        cursor.execute("""
            CREATE TABLE Break (
                breakID int NOT NULL AUTO_INCREMENT,
                shiftID int NOT NULL,
                breakStart datetime DEFAULT NULL,
                breakEnd datetime DEFAULT NULL,
                FOREIGN KEY (shiftID) REFERENCES ShiftTime(shiftID),
                PRIMARY KEY(breakID),
                INDEX idx_shift (shiftID)
            ) ENGINE = InnoDB;
        """)

        # Create announcements table
        cursor.execute("""
            CREATE TABLE announcements (
                announcementID int NOT NULL AUTO_INCREMENT,
                employerID varchar(100),
                announcement Text, 
                announcementTime datetime, 
                FOREIGN KEY (employerID) REFERENCES Account(userID), 
                PRIMARY KEY(announcementID),
                INDEX idx_employer (employerID)
            ) ENGINE = InnoDB;
        """)

        # Create notices table
        cursor.execute("""
            CREATE TABLE notices (
                employeeID varchar(100),
                announcementID int NOT NULL,
                FOREIGN KEY (employeeID) REFERENCES Account(userID),
                FOREIGN KEY (announcementID) REFERENCES announcements(announcementID),
                CONSTRAINT noticesPK PRIMARY KEY(employeeID, announcementID),
                INDEX idx_employee (employeeID)
            ) ENGINE = InnoDB;
        """)
        
        cursor.execute("""
            ALTER TABLE Company 
            ADD COLUMN id INT AUTO_INCREMENT UNIQUE;
        """)

        # Add id column to Employed table
        cursor.execute("""
            ALTER TABLE Employed 
            ADD COLUMN id INT AUTO_INCREMENT UNIQUE;
        """)

        # Add id column to Notices table
        cursor.execute("""
            ALTER TABLE Notices 
            ADD COLUMN id INT AUTO_INCREMENT UNIQUE;
        """)

        # Add id column to Expenses table
        cursor.execute("""
            ALTER TABLE Expenses 
            ADD COLUMN id INT AUTO_INCREMENT UNIQUE;
        """)
        cls.client = Client()
        cls.url = reverse('registerView')  # Ensure the correct URL name
        cls.role_employee = Roletable.objects.create(userrole='Employee')
        cls.role_employer = Roletable.objects.create(userrole='Employer')
        cls.account = Account.objects.create(userid='existing_user', firstname='John', lastname='Doe', userpass='hashedpassword')
        cls.company = Company.objects.create(employerid=cls.account, companyid='12345')
        

        
    def test_registration_missing_fields(cls):
        response = cls.client.post(cls.url, {})
        cls.assertContains(response, "Username is required.")
    
    def test_registration_existing_user(cls):
        response = cls.client.post(cls.url, {
            'userID': 'existing_user',
            'fname': 'John',
            'lname': 'Doe',
            'userPass': 'password123',
            'userPass2': 'password123',
            'companyID': '12345',
            'role': 'Employee'
        })
        cls.assertContains(response, "User already exists. Try another userID.")
    
    def test_registration_password_mismatch(cls):
        response = cls.client.post(cls.url, {
            'userID': 'newuser',
            'fname': 'Jane',
            'lname': 'Doe',
            'userPass': 'password123',
            'userPass2': 'password456',
            'companyID': '12345',
            'role': 'Employee'
        })
        cls.assertContains(response, "Passwords do not match.")

    def test_registration_password_too_short(cls):
        response = cls.client.post(cls.url, {
            'userID': 'newuser',
            'fname': 'Jane',
            'lname': 'Doe',
            'userPass': 'short',
            'userPass2': 'short',
            'companyID': '12345',
            'role': 'Employee'
        })
        cls.assertContains(response, "Password must be at least 8 characters long.")
    
    def test_successful_employee_registration(cls):
        response = cls.client.post(cls.url, {
            'userID': 'newemployee',
            'fname': 'Alice',
            'lname': 'Smith',
            'userPass': 'securepassword',
            'userPass2': 'securepassword',
            'companyID': '12345',
            'role': 'Employee'
        })
        cls.assertContains(response, "Employee created")
        user = Account.objects.get(userid='newemployee')
        cls.assertTrue(check_password('securepassword', user.userpass))
    
    def test_successful_employer_registration(cls):
        response = cls.client.post(cls.url, {
            'userID': 'newemployer',
            'fname': 'Bob',
            'lname': 'Brown',
            'userPass': 'securepassword',
            'userPass2': 'securepassword',
            'companyID': 'newComp',
            'role': 'Employer'
        })
        cls.assertContains(response, "Employer created")
        user = Account.objects.get(userid='newemployer')
        cls.assertTrue(check_password('securepassword', user.userpass))
        cls.assertTrue(Company.objects.filter(employerid=user).exists())

