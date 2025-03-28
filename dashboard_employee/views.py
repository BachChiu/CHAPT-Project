from django.views import View
from django.shortcuts import render

class EmployeeView(View):
    def get(self, request):
        return render(request, 'dashboard_employee/employee_dashboard.html')
