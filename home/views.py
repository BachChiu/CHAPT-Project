from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

def home(request):
    return render(request, 'home/home.html')

def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def clock_in(request):
    return render(request, 'clock/clock_in.html')

def reports(request):
    return render(request, 'reports/reports.html')

def login_view(request):
    return render(request, 'auth/login.html')

def register_view(request):
    return render(request, 'auth/register.html')
