
from pyexpat.errors import messages
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from common.models import Shifttime, Break


class dashboardView(TemplateView):
    def get(self, request, *args, **kwargs):
        if 'currentUser' not in request.session:
            return render(request, 'login/login.html', {"error": "Please login to access dashboard"})

        userRole = request.session.get('role')

        if userRole == 'Employer':
            return render(request, 'dashboard/employerDashboard.html')

        elif userRole == 'Employee':
            # Get current time for display
            current_time = timezone.now()

            # Get timesheet data
            employee_id = request.session.get('currentUser')
            timesheet_data = get_timesheet_data(employee_id) or []

            # Calculate total hours this week
            today = timezone.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            hours_this_week = sum(
                entry['totalHours']
                for entry in timesheet_data
                if entry['date'] >= start_of_week
            )

            # Get clock status from session
            clock_status = request.session.get('clock_status', 'out')
            shift_start = request.session.get('shift_start')
            break_start = request.session.get('break_start')

            # Calculate elapsed time if clocked in
            elapsed_time = None
            if clock_status in ['in', 'break'] and isinstance(shift_start, str):
                try:
                    shift_start_time = timezone.make_aware(
                        datetime.strptime(shift_start, '%H:%M:%S'),
                        timezone.get_current_timezone()
                    )
                    total_break_seconds = request.session.get('total_break_duration', 0)

                    if clock_status == 'in':
                        elapsed_seconds = (timezone.now() - shift_start_time).total_seconds() - total_break_seconds
                    elif clock_status == 'break' and isinstance(break_start, str):
                        break_start_time = timezone.make_aware(
                            datetime.strptime(break_start, '%H:%M:%S'),
                            timezone.get_current_timezone()
                        )
                        elapsed_seconds = (break_start_time - shift_start_time).total_seconds() - total_break_seconds
                    else:
                        elapsed_seconds = 0

                    hours, remainder = divmod(elapsed_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    elapsed_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                except Exception as e:
                    print("Elapsed time calculation error:", e)
                    elapsed_time = None

            # Format break duration
            total_break_seconds = request.session.get('total_break_duration', 0)
            hours, remainder = divmod(total_break_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            break_duration = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

            # Get today's activity
            today_activity = []
            if request.session.get('current_shift_id'):
                shift_id = request.session.get('current_shift_id')
                shift = Shifttime.objects.get(shiftid=shift_id)

                today_activity.append({
                    'action': 'Clock In',
                    'timestamp': shift.clockin
                })

                # Get all breaks for this shift
                breaks = Break.objects.filter(shiftid=shift_id)
                for break_record in breaks:
                    today_activity.append({
                        'action': 'Start Break',
                        'timestamp': break_record.breakstart
                    })

                    if break_record.breakend:
                        today_activity.append({
                            'action': 'End Break',
                            'timestamp': break_record.breakend
                        })

            context = {
                'current_time': current_time,
                'timesheet_data': timesheet_data,
                'hours_this_week': hours_this_week,
                'clock_status': clock_status,
                'shift_start': shift_start,
                'elapsed_time': elapsed_time,
                'break_duration': break_duration,
                'today_activity': today_activity
            }

            return render(request, 'dashboard/employeeDashboard.html', context)

        else:
            return render(request, 'login/login.html', {"error": "Invalid role?"})



# Clock In function
def clock_in(request):
    if request.method == 'POST':
        employee_id = request.session.get('currentUser')

        # Create new shift record
        new_shift = Shifttime(
            employeeid_id=employee_id,
            clockin=timezone.now(),
            clockout=None,
            breakduration=None
        )
        new_shift.save()

        # Store the shift ID in the session
        request.session['current_shift_id'] = new_shift.shiftid
        request.session['clock_status'] = 'in'
        request.session['shift_start'] = new_shift.clockin.strftime('%H:%M:%S')
        request.session['total_break_duration'] = 0

        return HttpResponseRedirect(reverse('dashboardView'))

    return HttpResponseRedirect(reverse('dashboardView'))


# Start Break function
def start_break(request):
    if request.method == 'POST':
        shift_id = request.session.get('current_shift_id')

        if not shift_id:
            return HttpResponseRedirect(reverse('dashboardView'))

        new_break = Break(
            shiftid_id=shift_id,
            breakstart=timezone.now(),
            breakend=None
        )
        new_break.save()

        request.session['current_break_id'] = new_break.breakid
        request.session['clock_status'] = 'break'
        request.session['break_start'] = new_break.breakstart.strftime('%H:%M:%S')

        return HttpResponseRedirect(reverse('dashboardView'))

    return HttpResponseRedirect(reverse('dashboardView'))


# End Break function
def end_break(request):
    if request.method == 'POST':
        break_id = request.session.get('current_break_id')

        if not break_id:
            return HttpResponseRedirect(reverse('dashboardView'))

        break_record = Break.objects.get(breakid=break_id)
        break_record.breakend = timezone.now()
        break_record.save()

        break_duration = (break_record.breakend - break_record.breakstart).total_seconds()
        total_break_duration = request.session.get('total_break_duration', 0)
        request.session['total_break_duration'] = total_break_duration + break_duration

        request.session['clock_status'] = 'in'
        request.session['current_break_id'] = None

        return HttpResponseRedirect(reverse('dashboardView'))

    return HttpResponseRedirect(reverse('dashboardView'))


# Clock Out function
def clock_out(request):
    if request.method == 'POST':
        shift_id = request.session.get('current_shift_id')
        if not shift_id:
            print("No active shift found in session.")
            return HttpResponseRedirect(reverse('dashboardView'))

        try:
            shift_record = Shifttime.objects.get(shiftid=shift_id)
        except Shifttime.DoesNotExist:
            print(f"Shift ID {shift_id} not found in DB.")
            return HttpResponseRedirect(reverse('dashboardView'))

        # Ensure clockout is assigned as a datetime object (timezone-aware)
        shift_record.clockout = timezone.now()

        # Debugging: Print out clockout before saving
        print(f"Clockout value before saving: {shift_record.clockout}")

        total_break_seconds = request.session.get('total_break_duration', 0)

        try:
            total_break_duration = timedelta(seconds=int(total_break_seconds))
            shift_record.breakduration = total_break_duration
        except Exception as e:
            print("Invalid total_break_duration:", total_break_seconds)
            print("Error:", e)

        shift_record.save()

        # Clear session variables
        request.session['current_shift_id'] = None
        request.session['current_break_id'] = None
        request.session['clock_status'] = 'out'
        request.session['shift_start'] = None
        request.session['break_start'] = None
        request.session['total_break_duration'] = 0

        print("Successfully clocked out. Session cleared.")

        return HttpResponseRedirect(reverse('dashboardView'))

    return HttpResponseRedirect(reverse('dashboardView'))

def get_timesheet_data(employee_id):
    shifts = Shifttime.objects.filter(employeeid_id=employee_id, clockout__isnull=False).order_by('-clockin')

    timesheet = []
    for shift in shifts:
        breaks = Break.objects.filter(shiftid=shift.shiftid, breakend__isnull=False)

        break_list = []
        for break_record in breaks:
            break_list.append({
                'id': break_record.breakid,
                'start': break_record.breakstart,
                'end': break_record.breakend,
                'duration': (break_record.breakend - break_record.breakstart).total_seconds()  # calculate duration in seconds
            })

        total_seconds = (shift.clockout - shift.clockin).total_seconds()

        # Manually calculate break duration in seconds (since breakduration is datetime.time)
        if shift.breakduration:
            break_seconds = shift.breakduration.hour * 3600 + shift.breakduration.minute * 60 + shift.breakduration.second
        else:
            break_seconds = 0

        total_hours = (total_seconds - break_seconds) / 3600

        timesheet.append({
            'id': shift.shiftid,
            'date': shift.clockin.date(),
            'clockIn': shift.clockin,
            'clockOut': shift.clockout,
            'breaks': break_list,
            'totalHours': round(total_hours, 2)
        })

    return timesheet

def logoutView(request):
    request.session.flush()
    return render(request, 'home/home.html', {"error": "Logout successfully"})
