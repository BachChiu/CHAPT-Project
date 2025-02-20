from django.contrib import admin
from django.urls import path, include
from attendance import views  # ✅ Correct! Import from your app folder

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('clock_in/', views.clock_in, name='clock_in'),
    path('clock_out/', views.clock_out, name='clock_out'),
]
