from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.HomeView.as_view()),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('clock-in/', views.clock_in, name='clock_in'),
    path('reports/', views.reports, name='reports'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
]
