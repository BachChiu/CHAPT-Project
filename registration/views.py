from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from common.models import Account, Company, Employed, Roletable
from django.contrib.auth.hashers import make_password

class RegisterView(TemplateView):
    template_name ='register/register.html'
    def post(self, request):
        #Grabbing data from the submitted form
        newUserID = request.POST.get("userID")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        newUserPass = request.POST.get("userPass")
        newUserPass = make_password(newUserPass)
        newCompany = request.POST.get("companyID")
        role = request.POST.get("role")
        if role:
            if role=="Employee":
                try:
                    Account.objects.get_or_create(userid=newUserID, firstname=fname, lastname = lname, userpass = newUserPass) #Create a new account, if it is already created then it just does nothing
                    account = Account.objects.get(userid = newUserID) #Grab the specific account that was just created/match the form as it is required for foreign key reference in Django (for the command below)
                    newCompanyObj = Company.objects.get(companyid=newCompany) #Grab specific company that the employee is to be assigned to
                    newrole = Roletable.objects.get(userrole=role) #Grab the user role
                    Employed.objects.get_or_create(employeeid=account, companyid=newCompanyObj, userrole = newrole, usersalary=0.0) #Create a new employee, if it is already created then does nothing
                    return render(request, self.template_name, {"error": "Employee created"})
                except Exception as e:
                    return render(request, self.template_name, {"error": f"That failed miserably {str(e)}"})
            elif role=="Employer":
                try:
                    Account.objects.get_or_create(userid=newUserID, firstname=fname, lastname = lname, userpass = newUserPass)#Create a new account, if it is already created then it just does nothing
                    account = Account.objects.get(userid = newUserID)#Grab the specific account that was just created/match the form as it is required for foreign key reference in Django (for the command below)
                    Company.objects.get_or_create(employerid=account,companyid=newCompany) #Create a new company, if it is already created then does nothing
                    return render(request, self.template_name, {"error": "Employer created"})
                except Exception as e:
                    return render(request, self.template_name, {"error": f"That failed miserably {str(e)}"})
            else:
                return render(request, self.template_name, {"error":"This should not have happened, ever"})
        return render(request, self.template_name, {"error": f"That failed miserably {str(e)}"})