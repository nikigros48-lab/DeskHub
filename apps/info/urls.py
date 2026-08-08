from django.urls import path

from apps.info.views import main_page, contacts, about, SelectCityView

app_name = 'info'

urlpatterns = [
    path('', main_page, name='main'),
    path("contacts/", contacts, name="contacts"),
    path("about/", about, name="about"),
    path("select-city/", SelectCityView.as_view(), name='select_city'),
]