from django.urls import path
from . import views
urlpatterns = [
    path('', views.ManagementView.as_view(), name='managementView'),
    path('schedule/', views.ManageScheduleView.as_view(), name='manageScheduleView')
]