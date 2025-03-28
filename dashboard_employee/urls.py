from django.urls import path
from . import views

urlpatterns = [
    path('employeeDash/', views.EmployeeView.as_view(), name='employeeView'),
]
