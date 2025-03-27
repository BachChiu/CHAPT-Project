from django.contrib import admin
from .models import BreakSession

@admin.register(BreakSession)
class BreakSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'break_start', 'break_end', 'is_active')
