from django.contrib import admin

from apps.coworkings.models import Coworking, City, Slot, Place


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name",]
    search_fields = ["name", "id"]
    ordering = ["id"]


@admin.register(Coworking)
class CoworkingAdmin(admin.ModelAdmin):
    list_display = ["city", "address",]
    list_filter = ["id", "city__name",]
    search_fields = ["id", "city__name",]
    ordering = ["id"]


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ["coworking", "type", "place_number","capacity", "is_blocked"]
    search_fields = ["coworking__city__name", "coworking__address", "place_number"]


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ["place", "start_datetime", "end_datetime",]
    search_fields = ["place__coworking__address", "place__place_number",]
