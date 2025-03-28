from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import BreakSession

@login_required
def start_break(request):
    break_session, created = BreakSession.objects.get_or_create(user=request.user, is_active=False)
    break_session.start_break()
    return JsonResponse({"message": "Break started successfully", "break_start": break_session.break_start})

@login_required
def end_break(request):
    break_session = get_object_or_404(BreakSession, user=request.user, is_active=True)
    break_session.end_break()
    return JsonResponse({"message": "Break ended successfully", "break_end": break_session.break_end})
