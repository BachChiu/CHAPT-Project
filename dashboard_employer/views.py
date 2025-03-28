from django.views import View
from django.shortcuts import render

class EmployerView(View):
    def get(self, request):
        return render(request, 'dashboard_employer/employer_dashboard.html')
