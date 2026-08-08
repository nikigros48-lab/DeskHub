from datetime import datetime, date
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from apps.reservation.models import Reservation


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class ReservationStatusView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
        data = {
            'id': reservation.id,
            'coworking_name': reservation.slot.place.coworking.name,
            'place': {
                'id': reservation.slot.place.id,
                'number': reservation.slot.place.place_number,
                'type': reservation.slot.place.get_type_display(),
            },
            'start': reservation.slot.start_datetime,
            'end': reservation.slot.end_datetime,
            'status': reservation.status,
            'status_display': reservation.get_status_display(),
            'created_at': reservation.created_at,
        }
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False, 'default': json_serial})