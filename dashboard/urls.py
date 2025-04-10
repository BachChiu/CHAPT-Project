from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboardView.as_view(), name='dashboardView'),
    path('logout/', views.logoutView, name='logoutView'),
    path('viewSchedule/<str:employee_id>/', views.view_emp_schedule, name='view_emp_scheduleView')
]