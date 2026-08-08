from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.registration.forms import LoginForm, RegistrationForm


class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm


class UserRegistrationView(CreateView):
    template_name = 'registration/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('auth:login')


class UserLogoutView(LogoutView):
    next_page = 'coworkings:list'