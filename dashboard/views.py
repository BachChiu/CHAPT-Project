from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
# Create your views here.
class dashboardView(TemplateView):
    def get(self, request, *args, **kwargs):
        if 'currentUser' not in request.session:
            return render(request, 'login/login.html', {"error": "Please login to access dashboard"})
        userRole = request.session.get('role')
        if userRole == 'Employer':
            return render(request, 'dashboard/employerDashboard.html')
        elif userRole == 'Employee':
            return render(request, 'dashboard/employeeDashboard.html')
        else:
             return render(request, 'login/login.html', {"error": "Invalid role?"})
        
def logoutView (request):
    request.session.flush()
    return render(request, 'home/home.html', {"error": "Logout successfully"})

