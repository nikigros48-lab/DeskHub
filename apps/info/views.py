from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView

from apps.coworkings.models import City


def main_page(request):
    return render(request, "info/main_page.html")


def contacts(request):
    return render(request, "info/contacts.html")


def about(request):
    return render(request, "info/about_us.html")


class CityListView(ListView):
    model = City
    context_object_name = 'cities'
    template_name = "info/choose_city.html"


class SelectCityView(View):
    def post(self, request):
        city_name = request.POST.get("city")
        if city_name:
            city = City.objects.filter(name=city_name).first()
            if city:
                request.session["selected_city_data"] = {
                    "id": city.id,
                    "name": city.name,
                }
                messages.success(request, f"Город {city.name} выбран!")
            else:
                messages.error(request, "Город не найден")
        else:
            request.session.pop("selected_city_data", None)
            messages.info(request, "Фильтр по городу сброшен")
        return redirect("coworkings:list")

    def get(self, request):
        cities = City.objects.all()
        return render(request, "info/choose_city.html", {"cities": cities})