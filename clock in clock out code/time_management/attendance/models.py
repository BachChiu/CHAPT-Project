from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class TimeRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    overtime = models.DurationField(default=timedelta())  # Store overtime as a duration

    def __str__(self):
        return f'{self.user.username} - {self.clock_in} to {self.clock_out}'

    def calculate_overtime(self):
        """Calculate overtime based on standard 8-hour workday."""
        standard_hours = timedelta(hours=8)  # Assume a standard 8-hour workday
        if self.clock_out and self.clock_in:
            worked_hours = self.clock_out - self.clock_in
            if worked_hours > standard_hours:
                self.overtime = worked_hours - standard_hours
            else:
                self.overtime = timedelta(0)
            self.save()
