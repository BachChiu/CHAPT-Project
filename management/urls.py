from django.urls import path
from . import views
urlpatterns = [
    path('', views.ManagementView.as_view(), name='managementView'),
    path('schedule/', views.ManageScheduleView.as_view(), name='manageScheduleView'),
    path('clockLogs/', views.ManageClockLogsView.as_view(), name='manageClockLogsView'),
    path('announcements/', views.ManageAnnouncementView.as_view(),name='manageAnnouncementView'),
    path('expenses/', views.ExpenseView.as_view(), name='expenseView')
]