from django.urls import path
from .views import RegisterView
from . import views
urlpatterns = [
    path('', views.RegisterView.as_view(), name='registerView'),
]