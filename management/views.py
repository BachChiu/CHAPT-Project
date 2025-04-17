import datetime
from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from common.models import Account, Compensation, Employed, Company, Expenses, Schedules, Shifttime, Announcements,Notices
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
        if 'scheduleFilter_employee' in request.session:
            employee_filter = request.session.get('scheduleFilter_employee')
            schedules = schedules.filter(employeeid=employee_filter)
            del request.session['scheduleFilter_employee'] #Just to clean it up and not have it get persisted through different filters.
        elif employee_filter != '' and employee_filter:
            schedules = schedules.filter(employeeid=employee_filter)
        if start_date_filter != '' and start_date_filter:
            schedules = schedules.filter(endtime__gte=make_aware(parse_datetime(start_date_filter)))
        if end_date_filter != '' and end_date_filter:
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
    
class ManageClockLogsView(TemplateView):
    template_name = 'management/clockLogs.html'

    def get(self, request):
        # Check if the user is logged in and is an Employer
        if 'currentUser' not in request.session or request.session.get('role') != 'Employer':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})

        # Get the current user (Employer)
        current_user = Account.objects.get(userid=request.session['currentUser'])

        # Get the company associated with the current employer
        company = Company.objects.get(employerid=current_user)

        # Fetch employees related to the company
        employees = Employed.objects.filter(companyid=company).select_related('employeeid')

        # Get filter values from the GET request
        employee_filter = request.GET.get('employee', '')
        start_time_filter = request.GET.get('start_time', '')
        end_time_filter = request.GET.get('end_time', '')

        # Retrieve Shifttime entries for all employees in the company
        shifttimes = Shifttime.objects.filter(employeeid__in=[e.employeeid for e in employees])

        # Apply employee filter if provided
        if employee_filter:
            shifttimes = shifttimes.filter(employeeid=employee_filter)

        # Apply start time filter if provided
        if start_time_filter:
            try:
                start_time = make_aware(parse_datetime(start_time_filter))
                shifttimes = shifttimes.filter(clockin__gte=start_time)
            except ValueError:
                pass  # Ignore invalid date formats

        # Apply end time filter if provided
        if end_time_filter:
            try:
                end_time = make_aware(parse_datetime(end_time_filter))
                shifttimes = shifttimes.filter(clockout__lte=end_time)
            except ValueError:
                pass  # Ignore invalid date formats

        # Fetch the corresponding compensation records
        compensations = Compensation.objects.filter(shiftid__in=[shift.shiftid for shift in shifttimes])

        # Map compensations to their respective Shifttime records
        clock_logs = []
        for shift in shifttimes:
            compensation = compensations.filter(shiftid=shift).first()  # Get the first compensation (or None if not found)
            clock_logs.append({
                'shift': shift,
                'compensation': compensation
            })

        return render(request, self.template_name, {
            'employees': employees,
            'clock_logs': clock_logs,
            'employee_filter': employee_filter,
            'start_time_filter': start_time_filter,
            'end_time_filter': end_time_filter,
        })

class ManageAnnouncementView(TemplateView):
    template_name = 'management/manageAnnouncements.html'

    def get(self, request):
        if 'currentUser' not in request.session or request.session.get('role') != 'Employer':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})

        current_user = Account.objects.get(userid=request.session['currentUser'])
        announcements = Announcements.objects.filter(employerid=current_user).order_by('-announcementtime')

        return render(request, self.template_name, {
            'announcements': announcements
        })

    def post(self, request):
        if 'currentUser' not in request.session or request.session.get('role') != 'Employer':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})

        current_user = Account.objects.get(userid=request.session['currentUser'])
        company = Company.objects.get(employerid=current_user)
        employees = Employed.objects.filter(companyid=company)

        # Delete announcement
        if 'delete_announcement' in request.POST:
            announcement_id = request.POST.get('delete_announcement')
            try:
                announcement = Announcements.objects.get(announcementid=announcement_id, employerid=current_user)
                Notices.objects.filter(announcementid=announcement).delete()
                announcement.delete()
            except Announcements.DoesNotExist:
                pass
            return redirect('manageAnnouncementView')

        # Post announcement
        announcement_text = request.POST.get('announcement')
        if announcement_text:
            try:
                announcement = Announcements.objects.create(
                    employerid=current_user,
                    announcement=announcement_text,
                    announcementtime=timezone.now()
                )

                Notices.objects.bulk_create([
                    Notices(employeeid=emp.employeeid, announcementid=announcement)
                    for emp in employees
                ])
            except Exception as e:
                announcements = Announcements.objects.filter(employerid=current_user).order_by('-announcementtime')
                return render(request, self.template_name, {
                    'announcements': announcements,
                    'error': f"Failed to post announcement: {str(e)}"
                })

        return redirect('manageAnnouncementView')
    
class ExpenseView(TemplateView):
    template_name = 'management/expenses.html'

    def get(self, request):
        if 'currentUser' not in request.session or request.session.get('role') != 'Employer':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})

        current_user = Account.objects.get(userid=request.session['currentUser'])
        company = Company.objects.get(employerid=current_user)
        employees = Employed.objects.filter(companyid=company)

        # Get filter values
        start_date_filter = request.GET.get('start_date', '')
        end_date_filter = request.GET.get('end_date', '')

        if 'reset_filter' in request.GET:
            try:
                del request.session['expenseFilter_start']
            except:
                pass
            try:
                del request.session['expenseFilter_end']
            except:
                pass
            start_date_filter = ''
            end_date_filter = ''

        # Filter expenses based on the filters provided
        expenses = Expenses.objects.filter(employerid=current_user)
        if start_date_filter != '' and start_date_filter:
            expenses = expenses.filter(expensedate__gte=make_aware(parse_datetime(start_date_filter)))
        if end_date_filter != '' and end_date_filter:
            expenses = expenses.filter(expensedate__lte=make_aware(parse_datetime(end_date_filter)))

        expenses = expenses.order_by('-expensedate')

        return render(request, self.template_name, {
            'employees': employees,
            'expenses': expenses,
            'start_date_filter': start_date_filter,
            'end_date_filter': end_date_filter,
        })

    def post(self, request):
        if 'currentUser' not in request.session or request.session.get('role') != 'Employer':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})

        current_user = Account.objects.get(userid=request.session['currentUser'])
        # Handle deleting an expense
        if 'delete_expense' in request.POST:
            expense_id = request.POST.get('delete_expense')
            try:
                expense = Expenses.objects.get(id=expense_id)
                expense.delete()
            except Expenses.DoesNotExist:
                pass

        return redirect('expenseView')