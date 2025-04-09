from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from common.models import Account, Company, Employed, Roletable
from django.contrib.auth.hashers import make_password, check_password
#from django.core.exceptions import ValidationError
from django.contrib.auth import logout

class RegisterView(TemplateView):
    template_name = 'register/register.html'

    def post(self, request):
        # Grabbing data from the submitted form
        newUserID = request.POST.get("userID")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        newUserPass = request.POST.get("userPass")
        newUserPass2 = request.POST.get("userPass2")  # Get confirmation password
        newCompany = request.POST.get("companyID")
        role = request.POST.get("role")
        
        # Null userID check
        if not newUserID:
            return render(request, self.template_name, {"error": "Username is required."})
        
        if not fname:
            return render(request, self.template_name, {"error": "First Name is required."})
        
        if not lname:
            return render(request, self.template_name, {"error": "Last Name is required."})

        #USerID Check
        if Account.objects.filter(userid=newUserID).exists():
            return render(request, self.template_name, {"error": "User already exists. Try another userID."})
       
       # Check password length (minimum 8 characters)
        if len(newUserPass) < 8:
            return render(request, self.template_name, {"error": "Password must be at least 8 characters long."})

       # Password match validation
        if newUserPass != newUserPass2:
            return render(request, self.template_name, {"error": "Passwords do not match."})

        # Hash password after confirmation
        newUserPass = make_password(newUserPass)

        if role:
            if role == "Employee":
                try:
                    # Create a new account if it doesn't exist
                    account, created = Account.objects.get_or_create(
                        userid=newUserID,
                        defaults={"firstname": fname, "lastname": lname, "userpass": newUserPass}
                    )
                    # If account already exists, update password
                    if not created:
                        account.userpass = newUserPass
                        account.save()

                    # Grab the newly created or existing account
                    account = Account.objects.get(userid=newUserID)
                    newCompanyObj = Company.objects.get(companyid=newCompany)  # Get company
                    newrole = Roletable.objects.get(userrole=role)  # Get user role

                    # Create an employee record if not already present
                    Employed.objects.get_or_create(
                        employeeid=account,
                        companyid=newCompanyObj,
                        userrole=newrole,
                        usersalary=0.0
                    )
                    return render(request, self.template_name, {"success": "Employee created"})
                except Exception as e:
                    return render(request, self.template_name, {"error": f"Registration failed: {str(e)}"})

            elif role == "Employer":
                try:
                    # Create or update account
                    account, created = Account.objects.get_or_create(
                        userid=newUserID,
                        defaults={"firstname": fname, "lastname": lname, "userpass": newUserPass}
                    )
                    if not created:
                        account.userpass = newUserPass
                        account.save()

                    # Grab account and create company
                    account = Account.objects.get(userid=newUserID)
                    Company.objects.get_or_create(employerid=account, companyid=newCompany)

                    return render(request, self.template_name, {"success": "Employer created"})
                except Exception as e:
                    return render(request, self.template_name, {"error": f"Registration failed: {str(e)}"})

            else:
                return render(request, self.template_name, {"error": "Invalid role selection."})

        return render(request, self.template_name, {"error": "Role is required."})

