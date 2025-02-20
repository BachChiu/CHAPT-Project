from django.urls import path
from . import views  

urlpatterns = [
    path('', views.home, name='home'),  # For the homepage
    path('clock_in/', views.clock_in, name='clock_in'),  # Clock in
    path('clock_out/', views.clock_out, name='clock_out'),  # Clock out
]
