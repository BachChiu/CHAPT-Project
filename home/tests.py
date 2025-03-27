from django.test import TestCase, Client
from django.urls import reverse
from django.db import connection
from home.models import Account, Roletable

class LoginViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Set up test DB schema
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
        cursor.execute("""
            CREATE TABLE Company (
                employerID varchar(100) NOT NULL,
                companyID varchar(100) NOT NULL UNIQUE,
                FOREIGN KEY (employerID) REFERENCES Account(userID),
                CONSTRAINT companyPK PRIMARY KEY (employerID, companyID)
            ) ENGINE = InnoDB;
        """)
        cursor.execute("""
            CREATE TABLE RoleTable (
                userRole varchar(100),
                PRIMARY KEY (userRole)
            ) ENGINE = InnoDB;
        """)
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
        cursor.execute("""
            CREATE TABLE Expenses (
                employerID varchar(100) NOT NULL,
                expenseDate DATE,
                expense decimal(19,4),
                FOREIGN KEY (employerID) REFERENCES Account(userID),
                CONSTRAINT expensesPK PRIMARY KEY (employerID, expenseDate)
            ) ENGINE = InnoDB;
        """)
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
        cursor.execute("ALTER TABLE Company ADD COLUMN id INT AUTO_INCREMENT UNIQUE;")
        cursor.execute("ALTER TABLE Employed ADD COLUMN id INT AUTO_INCREMENT UNIQUE;")
        cursor.execute("ALTER TABLE Notices ADD COLUMN id INT AUTO_INCREMENT UNIQUE;")
        cursor.execute("ALTER TABLE Expenses ADD COLUMN id INT AUTO_INCREMENT UNIQUE;")

        # Initialize simulated environment
        cls.client = Client()
        cls.url = reverse('loginView')  # Replace with your login view name
        cls.role_employee = Roletable.objects.create(userrole='Employee')
        cls.role_employer = Roletable.objects.create(userrole='Employer')
        cls.account = Account.objects.create(
            userid='testuser',
            firstname='Test',
            lastname='User',
            userpass='testpass123' 
        )

    def test_login_success(self):
        response = self.client.post(self.url, {
            'userid': 'testuser',
            'userpass': 'testpass123'
        })
        self.assertIn(response.status_code, [200, 302])
        self.assertNotContains(response, "Invalid login")

    def test_login_failure(self):
        response = self.client.post(self.url, {
            'userid': 'testuser',
            'userpass': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid login") 
