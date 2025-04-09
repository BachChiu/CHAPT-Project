from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from common.models import Account
from django.contrib.auth.hashers import check_password

# Create your views here.
class LoginView(TemplateView):
    template_name = 'login/login.html'
    def post(self, request):
        #Get result from post
        loginID = request.POST.get("userID")
        loginPass = request.POST.get("userPass")
        try:
            user = Account.objects.get(userid = loginID) #Find the account
        except Exception as e:
            return render(request, self.template_name, {"error": f"Account does not exist:"})
        userPass = user.userpass #Technically I could just throw it straight in check_password but anyway
        validPass = check_password(loginPass, userPass) #compare password
        if validPass:
            request.session['currentUser'] = user.userid
            
            if hasattr(user, 'employed'): 
#If an employed table entry exist, then its an employee (which might have different roles later), else if it have company entry, it can only be employer, but it can't be both.
                employed_object = user.employed 
                request.session['role'] = employed_object.userrole.userrole #Apparently since every reference is an object, had to do it twice to get the actual string
            elif hasattr(user, 'company'):
                request.session['role'] = 'Employer'
            return redirect(reverse('dashboardView'))
        else:
            return render(request, self.template_name, {"error": f"Wrong password"})