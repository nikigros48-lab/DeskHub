from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Имя пользователя"
        self.fields['password1'].label = "Пароль"
        self.fields['password2'].label = "Подтверждение пароля"
        self.fields['username'].help_text = "Обязательное поле. Не более 150 символов. Только буквы, цифры и @/./+/-/_ ."
        self.fields['password1'].help_text = "Ваш пароль должен содержать не менее 8 символов и не должен быть слишком простым."
        self.fields['password2'].help_text = "Введите тот же пароль для подтверждения."


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


