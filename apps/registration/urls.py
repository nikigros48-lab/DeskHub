from django.urls import path

from apps.registration.views import UserRegistrationView, UserLoginView, UserLogoutView

app_name = 'auth'


urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("register/", UserRegistrationView.as_view(), name="register"),
]