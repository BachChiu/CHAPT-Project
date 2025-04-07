from django.urls import path
from . import views
urlpatterns = [
    path('home/', views.HomeView.as_view(), name='homeView'),
    path('role/', views.roleView.as_view(), name='roleView'), #this will be deleted later
]