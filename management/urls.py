from django.urls import path
from . import views
urlpatterns = [
    path('', views.ManagementView.as_view(), name='managementView')
]