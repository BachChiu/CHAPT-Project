from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboardView.as_view(), name='dashboardView'),
]