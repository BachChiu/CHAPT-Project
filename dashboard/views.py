from django.shortcuts import redirect, render
from django.views.generic import TemplateView
# Create your views here.
class dashboardView(TemplateView):
    def get(self, request, *args, **kwargs):
        if 'currentUser' not in request.session:
            return redirect('loginView')
        userRole = request.session.get('role')
        if userRole == 'Employer':
            return render(request, 'dashboard/employerDashboard.html')
        elif userRole == 'Employee':
            return render(request, 'dashboard/employeeDashboard.html')
        else:
            return redirect('loginView')
        
        