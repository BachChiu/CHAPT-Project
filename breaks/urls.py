from django.urls import path
from .views import start_break, end_break

urlpatterns = [
    path('start-break/', start_break, name='start_break'),
    path('end-break/', end_break, name='end_break'),
]
