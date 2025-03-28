from django.shortcuts import render
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
            return render(request, self.template_name, {"error": f"Successful login"})
        else:
            return render(request, self.template_name, {"error": f"Wrong password"})