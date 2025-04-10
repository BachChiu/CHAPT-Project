from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from common.models import Employed, Account

class dashboardView(TemplateView):
    def get(self, request, *args, **kwargs):
        # Check if the user is logged in
        if 'currentUser' not in request.session:
            return render(request, 'login/login.html', {"error": "Please login to access dashboard"})

        # Get user role from the session
        userRole = request.session.get('role')

        if userRole == 'Employer':
            current_user_id = request.session.get('currentUser')  # Assuming this stores the logged-in employer's ID
            try:
                current_user = Account.objects.get(userid=current_user_id)
            except Account.DoesNotExist:
                return render(request, 'login/login.html', {"error": "Employer not found!"})

            # Get the list of employees associated with this employer's company
            employees = Employed.objects.filter(companyid__employerid=current_user).select_related('employeeid', 'userrole')

            # Render employer dashboard with employees data
            return render(request, 'dashboard/employerDashboard.html', {
                'current_user': current_user,
                'employees': employees
            })
        
        elif userRole == 'Employee':
            current_user_id = request.session.get('currentUser')
            try:
                current_user = Account.objects.get(userid=current_user_id)
            except Account.DoesNotExist:
                return render(request, 'login/login.html', {"error": "Employee not found!"})
            return render(request, 'dashboard/employeeDashboard.html',
            {
                'current_user':current_user       
            })

        else:
            return render(request, 'login/login.html', {"error": "Invalid role?"})

def view_emp_schedule(request, employee_id):
    request.session['scheduleFilter_employee'] = employee_id
    return redirect('manageScheduleView')  


def logoutView (request):
    request.session.flush()
    return render(request, 'login/login.html', {"error": "Logout successfully"})

