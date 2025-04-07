from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from common.models import Account, Employed, Company

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