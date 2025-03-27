from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from breaks.models import BreakSession

class BreakSessionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.break_session = BreakSession(user=cls.user)
        cls.break_session.save()


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
