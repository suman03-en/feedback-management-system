from django.views import View
from django.shortcuts import render, redirect, HttpResponse
from .forms import UserRegistrationForm


class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = "account/register.html"

    def get_form(self, *args, **kwargs):
        return self.form_class(*args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {"form": self.get_form()})

    def post(self, request):
        form = self.get_form(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("User registered successfully")
        return render(request, self.template_name, {"form": form})
