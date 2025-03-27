from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class BreakSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    break_start = models.DateTimeField(null=True, blank=True)
    break_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def start_break(self):
        if not self.is_active:
            self.break_start = now()
            self.is_active = True
            self.save()

    def end_break(self):
        if self.is_active:
            self.break_end = now()
            self.is_active = False
            self.save()

    def break_duration(self):
        if self.break_start and self.break_end:
            return (self.break_end - self.break_start).total_seconds() / 60
        return None

    def __str__(self):
        return f"{self.user.username} - Break Active: {self.is_active}"
