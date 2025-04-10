import datetime
from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from common.models import Account, Employed, Company, Schedules, Shifttime
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime

class ManagementView(TemplateView):
    template_name = 'management/management.html'

    def get(self, request):
        if 'currentUser' not in request.session:
            return render(request, 'login/login.html', {"error": "Please login to access this page"})

        userRole = request.session.get('role')
        if userRole != 'Employer':
            return render(request, 'login/login.html', {"error": "Invalid role"})

        currentUser = Account.objects.get(userid=request.session['currentUser']) #Get the account associated with the current user
        company = Company.objects.get(employerid=currentUser)#get the company that the employer is running
        employees = Employed.objects.filter(companyid=company).select_related('employeeid')#Get all employees in the company/under current user's jurisdiction

        return render(request, self.template_name, {'employees': employees})

    def post(self, request):
        if 'currentUser' not in request.session or request.session.get('role') != 'Employer':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})

        for key, value in request.POST.items():
            if key.startswith('salary_'):
                employee_id = key.replace('salary_', '')
                try:
                    employed = Employed.objects.get(employeeid=employee_id)
                    employed.usersalary = value
                    employed.save()
                except Employed.DoesNotExist:
                    continue  # skip if someone tampers with the form

        return redirect('managementView') #then just reload the page
    

class ManageScheduleView(TemplateView):
    template_name = 'management/schedule.html'

    def get(self, request):
        if 'currentUser' not in request.session or request.session.get('role') != 'Employer':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})

        current_user = Account.objects.get(userid=request.session['currentUser'])
        company = Company.objects.get(employerid=current_user)
        employees = Employed.objects.filter(companyid=company).select_related('employeeid')

        # Get filter values
        employee_filter = request.GET.get('employee', '')
        start_date_filter = request.GET.get('start_date', '')
        end_date_filter = request.GET.get('end_date', '')
        if 'reset_filter' in request.GET:
            try:
                del request.session['scheduleFilter_employee']
            except:
                pass
            try:
                del request.session['scheduleFilter_end']
            except:
                pass
            try:
                del request.session['scheduleFilter_start']
            except:
                pass
            employee_filter = ''
            start_date_filter = ''
            end_date_filter = ''
        # Filter schedules based on the filters provided
        schedules = Schedules.objects.filter(employeeid__in=[e.employeeid for e in employees])

        if employee_filter:
            schedules = schedules.filter(employeeid=employee_filter)
        if start_date_filter:
            schedules = schedules.filter(endtime__gte=make_aware(parse_datetime(start_date_filter)))
        if end_date_filter:
            schedules = schedules.filter(endtime__lte=make_aware(parse_datetime(end_date_filter)))
        
        schedules = schedules.order_by('starttime', 'employeeid')

        return render(request, self.template_name, {
            'employees': employees,
            'schedules': schedules,
            'employee_filter': employee_filter, 
            'start_date_filter': start_date_filter,
            'end_date_filter': end_date_filter,
        })

    def post(self, request):
        if 'currentUser' not in request.session or request.session.get('role') != 'Employer':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})

        current_user = Account.objects.get(userid=request.session['currentUser'])
        company = Company.objects.get(employerid=current_user)
        employees = Employed.objects.filter(companyid=company).select_related('employeeid')
        schedules = Schedules.objects.filter(employeeid__in=[e.employeeid for e in employees]).select_related('employeeid')
        #Deleting schedule
        if 'delete_schedule' in request.POST:
            schedule_id = request.POST.get('delete_schedule')
            try:
                schedule = Schedules.objects.get(scheduleid=schedule_id)
                schedule.delete()
            except Schedules.DoesNotExist:
                pass
        # Handle adding a new schedule
        if 'add_schedule' in request.POST:
            employee_id = request.POST.get('employee_id')
            start = request.POST.get('start_time')
            end = request.POST.get('end_time')

            try:
                start_time = make_aware(parse_datetime(start))
                end_time = make_aware(parse_datetime(end))

                if start_time >= end_time:
                    return render(request, self.template_name, {
                        "error": "Start time must be before end time.",
                        'employees': employees,
                        'schedules': schedules,
                    })

                overlapping_shifts = Schedules.objects.filter(employeeid=employee_id)
                for existing_shift in overlapping_shifts:
                    if(start_time < existing_shift.endtime and end_time > existing_shift.starttime):
                        return render(request, self.template_name, {
                            "error": "The new shift overlaps with an existing shift.",
                            "employees": employees,
                            "schedules": schedules,
                        })

                Schedules.objects.create(
                    employeeid=Account.objects.get(userid=employee_id),
                    starttime=start_time,
                    endtime=end_time
                )

            except Exception as e:
                return render(request, self.template_name, {"error": f"Error adding schedule: {str(e)}"})

        # Handle updating existing schedules
        for key in request.POST:
            if key.startswith('update_schedule'):
                schedule_id = request.POST.get('update_schedule')
                start = request.POST.get('start_time')
                end = request.POST.get('end_time')

                try:
                    schedule = Schedules.objects.get(scheduleid=schedule_id)

                    start_time = make_aware(parse_datetime(start))
                    end_time = make_aware(parse_datetime(end))

                    if start_time >= end_time:
                        return render(request, self.template_name, {
                            "error": "Start time must be before end time.",
                            'employees': employees,
                            'schedules': schedules,
                        })

                    overlapping_shifts = Schedules.objects.filter(employeeid=schedule.employeeid).exclude(scheduleid=schedule_id)
                    for existing_shift in overlapping_shifts:
                        if(start_time < existing_shift.endtime and end_time > existing_shift.starttime):
                            return render(request, self.template_name, {
                                "error": "The new shift overlaps with an existing shift.",
                                "employees": employees,
                                "schedules": schedules
                            })

                    schedule.starttime = start_time
                    schedule.endtime = end_time
                    schedule.save()

                except Schedules.DoesNotExist:
                    continue

        return redirect('manageScheduleView')