import datetime
import json
from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from common.models import Account, Compensation, Employed, Company, Notices, Schedules, Shifttime
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime

class PersonalScheduleView(TemplateView):
    template_name = 'employee/personalSchedule.html'
    def get(self, request):
        if 'currentUser' not in request.session or request.session.get('role') != 'Employee':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})
        currentUser = Account.objects.get(userid=request.session['currentUser'])
        start_date_filter = request.GET.get('start_date', '')
        end_date_filter = request.GET.get('end_date', '')
        if 'reset_filter' in request.GET:
            try: #Just here in case I need to use it later, these sessions aren't quite necessary yet.
                del request.session['scheduleFilter_end']
            except:
                pass
            try:
                del request.session['scheduleFilter_start']
            except:
                pass
            start_date_filter = ''
            end_date_filter = ''
        schedules = Schedules.objects.filter(employeeid = currentUser)
        if start_date_filter != '' and start_date_filter:
            schedules = schedules.filter(endtime__gte=make_aware(parse_datetime(start_date_filter)))
        if end_date_filter != '' and end_date_filter:
            schedules = schedules.filter(endtime__lte=make_aware(parse_datetime(end_date_filter)))
        schedules = schedules.order_by('starttime')
        return render(request, self.template_name, 
        {
             'currentUser': currentUser,
             'start_date_filter': start_date_filter,
             'end_date_filter':end_date_filter,  
             'schedules': schedules,                
        })

class PersonalTimesheetView(TemplateView): 
    template_name = 'employee/personalTimesheet.html'

    def get(self, request):
        # Check if the user is authenticated and an Employee
        if 'currentUser' not in request.session or request.session.get('role') != 'Employee':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})

        currentUser = Account.objects.get(userid=request.session['currentUser'])
        start_date_filter = request.GET.get('start_date', '')
        end_date_filter = request.GET.get('end_date', '')

        # Reset filters if reset_filter is in the GET request
        if 'reset_filter' in request.GET:
            try:
                del request.session['timesheetFilter_start']
            except KeyError:
                pass
            try:
                del request.session['timesheetFilter_end']
            except KeyError:
                pass
            start_date_filter = ''
            end_date_filter = ''

        # Filter shifts for the current user
        shifts = Shifttime.objects.filter(employeeid=currentUser)

        if start_date_filter:
            shifts = shifts.filter(clockin__gte=make_aware(parse_datetime(start_date_filter)))
        if end_date_filter:
            shifts = shifts.filter(clockout__lte=make_aware(parse_datetime(end_date_filter)))

        # Order shifts by clockin date
        shifts = shifts.order_by('-clockin')

        # Retrieve compensation for each shift (checking for existence of compensation)
        shift_data = []
        for shift in shifts:
            compensation = Compensation.objects.filter(shiftid=shift).first()  # Use filter().first() to get the first match or None
            
            shift_data.append({
                'shift': shift,
                'compensation': compensation
            })

        return render(request, self.template_name, {
            'currentUser': currentUser,
            'start_date_filter': start_date_filter,
            'end_date_filter': end_date_filter,
            'shift_data': shift_data,
        })
        
class NoticeView(TemplateView):
    template_name = 'employee/notices.html'

    def get(self, request):
        if 'currentUser' not in request.session or request.session.get('role') != 'Employee':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})

        current_user = Account.objects.get(userid=request.session['currentUser'])

        # Fetch notices for the logged-in employee
        notices = Notices.objects.filter(employeeid=current_user).select_related('announcementid', 'announcementid__employerid').order_by('-announcementid__announcementtime')

        return render(request, self.template_name, {
            'notices': notices
        })