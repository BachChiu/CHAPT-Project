from django.utils import timezone
from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from common.models import Employed, Account, Shifttime, Break
from django.contrib import messages
from datetime import timedelta
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
            current_shift = Shifttime.objects.filter(employeeid=current_user, clockout__isnull=True).order_by('-clockin').first()
            clock_status = "Clocked Out"
            on_break = False
            if current_shift:
                clock_status = "Clocked In"
                on_break = Break.objects.filter(shiftid=current_shift, breakend__isnull=True).exists()
            return render(request, 'dashboard/employeeDashboard.html',
            {
                'current_user':current_user,
                'clock_status': clock_status,
                'on_break': on_break       
            })

        else:
            return render(request, 'login/login.html', {"error": "Invalid role?"})

def view_emp_schedule(request, employee_id):
    request.session['scheduleFilter_employee'] = employee_id
    return redirect('manageScheduleView')  


def logoutView (request):
    request.session.flush()
    return render(request, 'login/login.html', {"error": "Logout successfully"})

def clock_action(request):
    userRole = request.session.get('role')
    if not userRole == 'Employee':
        messages.error(request, "Please log in to a valid account.")
        return redirect('loginView')
    user_id = request.session.get('currentUser')
    action = request.POST.get("action")
    current_user = Account.objects.get(userid=user_id)

    # Get latest shift (if any) that hasn't been clocked out
    current_shift = Shifttime.objects.filter(employeeid=current_user, clockout__isnull=True).order_by('-clockin').first()

    if action == "clock_in":
        if current_shift:
            messages.error(request, "You're already clocked in.")
        else:
            Shifttime.objects.create(employeeid=current_user, clockin=timezone.now())
            messages.success(request, "Clocked in successfully.")
    
    elif action == "take_break":
        if not current_shift:
            messages.error(request, "You need to clock in first.")
        else:
            active_break = Break.objects.filter(shiftid=current_shift, breakend__isnull=True).first()
            if active_break:
                # End break
                active_break.breakend = timezone.now()
                active_break.save()
                messages.success(request, "Break ended.")
            else:
                # Start break
                Break.objects.create(shiftid=current_shift, breakstart=timezone.now())
                messages.success(request, "Break started.")

    elif action == "clock_out":
        if not current_shift:
            messages.error(request, "You're not clocked in.")
        else:
            try:
                active_break = Break.objects.filter(shiftid=current_shift, breakend__isnull=True).first()
                if active_break:
                    active_break.breakend = timezone.now()
                    active_break.save()
            except:
                pass
            current_shift.clockout = timezone.now()
            current_shift.save()

            # Calculate break duration (if any breaks recorded)
            total_break_seconds = 0
            breaks = Break.objects.filter(shiftid=current_shift, breakstart__isnull=False, breakend__isnull=False)
            for b in breaks:
                total_break_seconds += (b.breakend - b.breakstart).total_seconds()

            # Convert total seconds to hours, minutes, and seconds for MySQL's TIME format
            hours, remainder = divmod(total_break_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Store the break duration as a TIME string (e.g., 'HH:MM:SS')
            current_shift.breakduration = f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'
            current_shift.save()

            messages.success(request, "Clocked out successfully.")

    return redirect('dashboardView')