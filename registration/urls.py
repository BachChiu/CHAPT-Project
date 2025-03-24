from django.urls import path
from .views import RegisterView
from . import views
urlpatterns = [
    path('', views.RegisterView.as_view(), name='registerView'),
    #path('', RegisterView.as_view(), name="register"),
    #path("login/", LoginView.as_view(), name="login"),
    #path("logout/", LogoutView.as_view(), name="logout"),
]