import datetime
import json
from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from common.models import Account, Employed, Company, Schedules, Shifttime
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
    