from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboardView.as_view(), name='dashboardView'),
    path('logout/', views.logoutView, name='logoutView'),
    # Add new clock action URLs
    path('clock-in/', views.clock_in, name='clock_in'),
    path('start-break/', views.start_break, name='start_break'),
    path('end-break/', views.end_break, name='end_break'),
    path('clock-out/', views.clock_out, name='clock_out'),
]