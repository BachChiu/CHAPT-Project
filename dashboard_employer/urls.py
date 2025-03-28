from django.urls import path
from . import views

urlpatterns = [
    path('employerDash/', views.EmployerView.as_view(), name='employerView'),
]
