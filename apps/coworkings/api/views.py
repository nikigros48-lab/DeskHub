from datetime import datetime, date
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.coworkings.models import Coworking, Slot


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class CoworkingListView(View):
    """API: список коворкингов с фильтром по городу (по названию)"""
    def get(self, request):
        city_name = request.GET.get('city')
        queryset = Coworking.objects.select_related('city')
        if city_name:
            queryset = queryset.filter(city__name__icontains=city_name)

        data = []
        for cw in queryset:
            data.append({
                'id': cw.id,
                'name': cw.name,
                'address': cw.address,
                'city': cw.city.name,
            })
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False, 'default': json_serial})


class CoworkingDetailAPIView(View):
    def get(self, request, pk):
        coworking = get_object_or_404(Coworking, pk=pk)
        date_str = request.GET.get('date')
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format, use YYYY-MM-DD'}, status=400)
        else:
            selected_date = timezone.now().date()

        places = coworking.places.filter(is_blocked=False)
        slots_data = []
        for place in places:
            slots = Slot.objects.filter(
                place=place,
                start_datetime__date__lte=selected_date,
                end_datetime__date__gte=selected_date
            )
            for slot in slots:
                is_booked = slot.reservations.filter(
                    status__in=['confirmed', 'pending']
                ).exists()
                slots_data.append({
                    'place_id': place.id,
                    'place_number': place.place_number,
                    'place_type': place.get_type_display(),
                    'capacity': place.capacity,
                    'start': slot.start_datetime,
                    'end': slot.end_datetime,
                    'is_booked': is_booked,
                })

        data = {
            'id': coworking.id,
            'name': coworking.name,
            'address': coworking.address,
            'city': coworking.city.name,
            'selected_date': selected_date,
            'slots': slots_data,
        }
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False, 'default': json_serial})