from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'slot', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'slot__place__coworking__name']