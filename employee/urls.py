from django.urls import path
from . import views
urlpatterns = [
    path('', views.PersonalScheduleView.as_view(), name='personalScheduleView'),
]