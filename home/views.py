from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from common.models import Roletable
# Create your views here.
class HomeView(TemplateView):
    template_name = 'home/home.html'

#Just for testing connection with the database and the ORM, not intended for usage later
class roleView(TemplateView):
    template_name = 'role/role.html'
    def post(self, request):
        role = request.POST.get("role")
        if role:
            try:
                Roletable.objects.get(userrole=role)
                return render(request, self.template_name, {"error": "Role already existed"})
            except:
                Roletable.objects.create(userrole=role)
                return render(request, self.template_name, {"error": "Role is created"})
        return render(request, self.template_name, {"error": "Role is required!"})
            
                    