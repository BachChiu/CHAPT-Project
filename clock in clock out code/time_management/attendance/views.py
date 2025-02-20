from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import TimeRecord

# Clock in view
@login_required
def clock_in(request):
    if request.method == 'POST':
        # Check if the user is already clocked in
        if not TimeRecord.objects.filter(user=request.user, clock_out=None).exists():
            time_record = TimeRecord(user=request.user, clock_in=timezone.now())
            time_record.save()
        return redirect('home')  # Redirect to home page or wherever you want

    return render(request, 'clockinout/clock_in.html')

# Clock out view
@login_required
def clock_out(request):
    if request.method == 'POST':
        # Find the clock-in record for the user
        time_record = TimeRecord.objects.filter(user=request.user, clock_out=None).first()
        if time_record:
            time_record.clock_out = timezone.now()
            time_record.calculate_overtime()  # Calculate overtime after clocking out
            time_record.save()
        return redirect('home')  # Redirect to home page or wherever you want

    return render(request, 'clockinout/clock_out.html')

# Home page showing clock-in/out records and overtime
@login_required
def home(request):
    records = TimeRecord.objects.filter(user=request.user)
    return render(request, 'clockinout/home.html', {'records': records})
