from django.test import TestCase
from django.db import connection
# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now, timedelta
from common.models import Account, Company, Employed, Roletable, Break

class BreakSessionTests(TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test data for all test methods."""
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
        cls.url = reverse('homeView')  # Ensure the correct URL name
        cls.role_employee = Roletable.objects.create(userrole='Employee')
        cls.role_employer = Roletable.objects.create(userrole='Employer')
        cls.account = Account.objects.create(userid='existing_user', firstname='John', lastname='Doe', userpass='hashedpassword')
        cls.company = Company.objects.create(employerid=cls.account, companyid='12345')

    def test_start_break(self):
        """Test if start_break method sets break_start and activates the session."""
        self.break_session.start_break()
        self.assertTrue(self.break_session.is_active)
        self.assertIsNotNone(self.break_session.break_start)

    def test_end_break(self):
        """Test if end_break method sets break_end and deactivates the session."""
        self.break_session.start_break()
        self.break_session.end_break()
        self.assertFalse(self.break_session.is_active)
        self.assertIsNotNone(self.break_session.break_end)

    def test_break_duration(self):
        """Test if break_duration calculates time correctly."""
        self.break_session.start_break()
        self.break_session.break_end = self.break_session.break_start + timedelta(minutes=30)
        self.break_session.save()
        self.assertEqual(self.break_session.break_duration(), 30)

    def test_break_duration_without_end(self):
        """Test break_duration when break_end is None (should return None)."""
        self.break_session.start_break()
        self.assertIsNone(self.break_session.break_duration())

    def test_str_method(self):
        """Test the __str__ method returns the expected string."""
        expected_str = f"{self.break_session.user.username} - Break Active: {self.break_session.is_active}"
        self.assertEqual(str(self.break_session), expected_str)
