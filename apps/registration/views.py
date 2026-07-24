from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.generic import CreateView

from apps.registration.forms import LoginForm, RegistrationForm


class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm


class UserRegistrationView(CreateView):
    template_name = 'registration/registration.html'
    form_class = RegistrationForm


class UserLogoutView(LogoutView):
    next_page = 'coworkings:coworking_list'


# def logout_view(request:HttpRequest) -> HttpResponse:
#     logout(request)
#     print("logout")
#     return redirect("coworkings:coworking_list")