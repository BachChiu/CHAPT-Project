from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('breaks/', include('breaks.urls')),  # Include breaks app URLs
]
