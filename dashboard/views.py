from django.utils import timezone
from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from common.models import Compensation, Employed, Account, Expenses, Shifttime, Break
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.hashers import check_password,make_password

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
            now = timezone.now()
            try:
                active_break = Break.objects.filter(shiftid=current_shift, breakend__isnull=True).first()
                if active_break:
                    active_break.breakend = now
                    active_break.save()
            except:
                pass
            current_shift.clockout = timezone.now()
            current_shift.save()
            total_shift_seconds = (current_shift.clockout - current_shift.clockin).total_seconds()
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
            actualWorkHours = Decimal(total_shift_seconds - total_break_seconds)/Decimal(3600)
        
            current_year, current_week, _ = current_shift.clockin.isocalendar()
            currentWeekShifts = Shifttime.objects.filter(employeeid=current_user, clockin__isnull=False,clockout__isnull=False, clockin__week = current_week, clockin__year = current_year).exclude(shiftid=current_shift.shiftid)
            total_week_seconds = 0
            for shift in currentWeekShifts:
                shiftSeconds = (shift.clockout - shift.clockin).total_seconds()
                h,m,s = shift.breakduration.hour, shift.breakduration.minute, shift.breakduration.second
                shiftBreakTime = h * 3600 + m * 60 + s
                total_week_seconds += shiftSeconds - shiftBreakTime
            currentWeekHours = Decimal(total_week_seconds) / Decimal(3600)
            regularHours = Decimal(min(40 - currentWeekHours, actualWorkHours))
            overtimeHours = Decimal(max(0, actualWorkHours - regularHours))
            employee = Employed.objects.get(employeeid = current_user)
            userSalary = employee.usersalary
            shiftCompensation = Decimal(regularHours) * userSalary + Decimal(overtimeHours) * userSalary * Decimal(1.5)
            compensationEntry = Compensation.objects.create(shiftid=current_shift, employeeid = current_user, shiftcompensation = shiftCompensation)
            try:
                workDate = current_shift.clockin.date()
                company = employee.companyid
                employer = company.employerid
                expenseEntry = Expenses.objects.filter(employerid =employer, expensedate = workDate).first()
                if expenseEntry:
                    expenseEntry.expense += shiftCompensation
                    expenseEntry.save()
                else:
                    Expenses.objects.create(employerid=employer, expensedate = workDate, expense = shiftCompensation)
            except:
                #So since the shift is invalid for whatever reason, don't want it to clog the compensation table
                #Just delete and then recalculate later
                compensationEntry.delete()
            messages.success(request, "Clocked out successfully.")

    return redirect('dashboardView')

class profileView(TemplateView):
    template_name = 'dashboard/profile.html'
    def get(self, request):
        # Check if the user is logged in
        if 'currentUser' not in request.session:
            return render(request, 'login/login.html', {"error": "Please login to access dashboard"})
        userRole = request.session.get('role')
        current_user_id = request.session.get('currentUser')  # Assuming this stores the logged-in employer's ID
        try:
            current_user = Account.objects.get(userid=current_user_id)
            first_name = current_user.firstname
            last_name = current_user.lastname
        except Account.DoesNotExist:
            return render(request, 'login/login.html', {"error": "User not found!"})
        return render(request, 'dashboard/profile.html',
        {
                'current_user':current_user,
                'role': userRole,
                'firstName': first_name,
                'lastName':last_name,
        })
    def post(self, request):
        current_user_id = request.session.get('currentUser')
        try:
            current_user = Account.objects.get(userid=current_user_id)
        except Account.DoesNotExist:
            return render(request, 'login/login.html', {"error": "User not found!"})
        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        confirm_password = request.POST.get('confirmPassword')

        errors = []

        # Update name if changed
        if first_name and first_name != current_user.firstname:
            current_user.firstname = first_name
        if last_name and last_name != current_user.lastname:
            current_user.lastname = last_name

        # Handle password change
        if current_password or new_password or confirm_password:
            if not all([current_password, new_password, confirm_password]):
                errors.append("All password fields must be filled to change password.")
            elif not check_password(current_password, current_user.userpass):
                errors.append("Current password is incorrect.")
            elif len(new_password) < 8:
                errors.append("New password must be at least 8 characters long.")
            elif new_password != confirm_password:
                errors.append("New passwords do not match.")
            else:
                current_user.userpass = make_password(new_password)

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            current_user.save()
            messages.success(request, "Profile updated successfully!")

        return redirect('profileView')
        