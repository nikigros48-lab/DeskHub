from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import ListView, DetailView
from apps.coworkings.models import Coworking, Slot, Place
from apps.reservation.models import Reservation
from django.db.models import OuterRef, Exists


class CoworkingListView(ListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_date = None
        self.place_type = None
        self.time_start = None
        self.time_end = None

    model = Coworking
    context_object_name = 'coworkings'
    template_name = "coworkings/coworkings_list.html"

    def get_queryset(self):
        queryset = Coworking.objects.all()

        city_data = self.request.session.get("selected_city_data")
        if city_data:
            city_id = city_data.get("id")
            if city_id:
                queryset = queryset.filter(city_id=city_id)

        date_str = self.request.GET.get('date')
        if date_str:
            try:
                self.filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.filter_date = timezone.now().date()
        else:
            self.filter_date = timezone.now().date()

        place_type = self.request.GET.get('type')
        if place_type in ['desk', 'meeting']:
            self.place_type = place_type
        else:
            self.place_type = None

        time_start = self.request.GET.get('time_start')
        time_end = self.request.GET.get('time_end')
        if time_start:
            try:
                self.time_start = datetime.strptime(time_start, '%H:%M').time()
            except ValueError:
                self.time_start = None
        else:
            self.time_start = None
        if time_end:
            try:
                self.time_end = datetime.strptime(time_end, '%H:%M').time()
            except ValueError:
                self.time_end = None
        else:
            self.time_end = None

        if self.filter_date and (self.time_start or self.time_end):
            if self.time_start:
                start_dt = datetime.combine(self.filter_date, self.time_start)
            else:
                start_dt = datetime.combine(self.filter_date, datetime.min.time())

            if self.time_end:
                end_dt = datetime.combine(self.filter_date, self.time_end)
            else:
                end_dt = datetime.combine(self.filter_date, datetime.max.time())

            free_places = Place.objects.filter(
                coworking=OuterRef('pk'),
                is_blocked=False,
            ).exclude(
                slots__reservations__status__in=['confirmed', 'pending'],
                slots__start_datetime__lt=end_dt,
                slots__end_datetime__gt=start_dt,
            ).distinct()

            if self.place_type:
                free_places = free_places.filter(type=self.place_type)

            queryset = queryset.filter(Exists(free_places))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_date'] = getattr(self, 'filter_date', timezone.now().date())
        context['place_type'] = getattr(self, 'place_type', None)
        context['time_start'] = getattr(self, 'time_start', None)
        context['time_end'] = getattr(self, 'time_end', None)
        return context


class CoworkingDetailView(DetailView):
    model = Coworking
    context_object_name = 'coworking'
    template_name = "coworkings/coworking_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        coworking = self.object

        date_str = self.request.GET.get('date')
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = timezone.now().date()
        else:
            selected_date = timezone.now().date()

        context['selected_date'] = selected_date
        context['previous_date'] = selected_date - timedelta(days=1)
        context['next_date'] = selected_date + timedelta(days=1)

        places = coworking.places.filter(is_blocked=False)
        context['places'] = places

        booked_slots = {}
        for place in places:
            slots_on_date = Slot.objects.filter(
                place=place,
                start_datetime__date__lte=selected_date,
                end_datetime__date__gte=selected_date
            )
            reserved = Reservation.objects.filter(
                slot__in=slots_on_date,
                status__in=['confirmed', 'pending']
            ).select_related('slot')
            intervals = [(res.slot.start_datetime, res.slot.end_datetime) for res in reserved]
            booked_slots[place.id] = intervals
        context['booked_slots'] = booked_slots

        form_data = {
            'place': self.request.GET.get('place', ''),
            'start': self.request.GET.get('start', ''),
            'end': self.request.GET.get('end', ''),
        }
        if not form_data['place'] and not form_data['start'] and not form_data['end']:
            form_data = self.request.session.get('booking_form_data', {})
        context['form_data'] = form_data

        return context


def get_slots_partial(request, pk):
    coworking = get_object_or_404(Coworking, pk=pk)

    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    previous_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)

    places = coworking.places.filter(is_blocked=False)

    booked_slots = {}
    for place in places:
        slots_on_date = Slot.objects.filter(
            place=place,
            start_datetime__date__lte=selected_date,
            end_datetime__date__gte=selected_date
        )
        reserved = Reservation.objects.filter(
            slot__in=slots_on_date,
            status__in=['confirmed', 'pending']
        ).select_related('slot')
        intervals = [(res.slot.start_datetime, res.slot.end_datetime) for res in reserved]
        booked_slots[place.id] = intervals

    context = {
        'places': places,
        'selected_date': selected_date,
        'previous_date': previous_date,
        'next_date': next_date,
        'booked_slots': booked_slots,
    }
    html = render_to_string('coworkings/_slots_partial.html', context)
    return JsonResponse({'html': html})