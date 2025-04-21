'''
 This is here so i can deal with some extra stuff regarding keeping the filter after updating and stuff later, the point is this code was suppose to
 allow update and adding shift, whilst keeping the filter on the page the same (or update the filter at the same time as updating/adding shift). However,
 despite keeping the filter consistent, it fails to update the filter unless I click apply filter, but I want it to apply along with whatever changes I make instead,
 so for now this code is left here so I can revisit when I have time.
class ManageScheduleView(TemplateView):
    template_name = 'management/schedule.html'

    def get(self, request):
        if 'currentUser' not in request.session or request.session.get('role') != 'Employer':
            return render(request, 'login/login.html', {"error": "Unauthorized access"})

        current_user = Account.objects.get(userid=request.session['currentUser'])
        company = Company.objects.get(employerid=current_user)
        employees = Employed.objects.filter(companyid=company).select_related('employeeid')
        employee_filter = request.GET.get('employee', '')
        start_date_filter = request.GET.get('start_date', '')
        end_date_filter = request.GET.get('end_date', '')
        if employee_filter == '' and 'scheduleFilter_employee' in request.session:
            employee_filter = request.session['scheduleFilter_employee'] 
        else:
            request.session['scheduleFilter_employee'] = employee_filter
        if start_date_filter == '' and 'scheduleFilter_start' in request.session:
            start_date_filter = request.session['scheduleFilter_start']
        else:
            request.session['scheduleFilter_start'] = start_date_filter
        if end_date_filter == '' and 'scheduleFilter_end' in request.session:
            end_date_filter = request.session['scheduleFilter_end']
        else:
            request.session['scheduleFilter_end'] = end_date_filter
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
        employee_filter = request.GET.get('employee', '')
        start_date_filter = request.GET.get('start_date', '')
        end_date_filter = request.GET.get('end_date', '')
        if employee_filter == '' and 'scheduleFilter_employee' in request.session:
            employee_filter = request.session['scheduleFilter_employee'] 
        else:
            request.session['scheduleFilter_employee'] = employee_filter
        if start_date_filter == '' and 'scheduleFilter_start' in request.session:
            start_date_filter = request.session['scheduleFilter_start']
        else:
            request.session['scheduleFilter_start'] = start_date_filter
        if end_date_filter == '' and 'scheduleFilter_end' in request.session:
            end_date_filter = request.session['scheduleFilter_end']
        else:
            request.session['scheduleFilter_end'] = end_date_filter
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
                        'employee_filter': employee_filter, 
                        'start_date_filter': start_date_filter,
                        'end_date_filter': end_date_filter,
                    })

                overlapping_shifts = Schedules.objects.filter(employeeid=employee_id)
                for existing_shift in overlapping_shifts:
                    if(start_time < existing_shift.endtime and end_time > existing_shift.starttime):
                        return render(request, self.template_name, {
                            "error": "The new shift overlaps with an existing shift.",
                            "employees": employees,
                            "schedules": schedules,
                            'employee_filter': employee_filter, 
                            'start_date_filter': start_date_filter,
                            'end_date_filter': end_date_filter,
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
                            'employee_filter': employee_filter, 
                            'start_date_filter': start_date_filter,
                            'end_date_filter': end_date_filter,
                        })

                    overlapping_shifts = Schedules.objects.filter(employeeid=schedule.employeeid).exclude(scheduleid=schedule_id)
                    for existing_shift in overlapping_shifts:
                        if(start_time < existing_shift.endtime and end_time > existing_shift.starttime):
                            return render(request, self.template_name, {
                                "error": "The new shift overlaps with an existing shift.",
                                "employees": employees,
                                "schedules": schedules,
                                'employee_filter': employee_filter, 
                                'start_date_filter': start_date_filter,
                                'end_date_filter': end_date_filter,
                            })

                    schedule.starttime = start_time
                    schedule.endtime = end_time
                    schedule.save()

                except Schedules.DoesNotExist:
                    continue

        return redirect('manageScheduleView')
        
       
        '''