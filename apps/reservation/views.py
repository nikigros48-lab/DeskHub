from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, ListView
from apps.coworkings.models import Slot
from .forms import ReservationForm
from .models import Reservation

class CreateReservationView(LoginRequiredMixin, FormView):
    template_name = 'reservation/create.html'
    form_class = ReservationForm
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        place = form.cleaned_data['place']
        start = form.cleaned_data['start_datetime']
        end = form.cleaned_data['end_datetime']

        conflicting_reservations = Reservation.objects.filter(
            slot__place=place,
            slot__start_datetime__lt=end,
            slot__end_datetime__gt=start,
            status__in=['confirmed', 'pending']
        )
        if conflicting_reservations.exists():
            form.add_error(None, "Это время уже занято другим бронированием.")
            self.request.session['booking_form_data'] = {
                'place': str(place.id),
                'start': start.isoformat(),
                'end': end.isoformat(),
            }
            return self.form_invalid(form)

        with transaction.atomic():
            slot = Slot.objects.create(
                place=place,
                start_datetime=start,
                end_datetime=end
            )
            Reservation.objects.create(
                user=self.request.user,
                slot=slot,
                status='pending'
            )

        if 'booking_form_data' in self.request.session:
            del self.request.session['booking_form_data']

        messages.success(self.request, "Заявка на бронирование создана! Ожидайте подтверждения.")
        return super().form_valid(form)

    def form_invalid(self, form):
        if form.errors:
            self.request.session['booking_form_data'] = {
                'place': self.request.POST.get('place'),
                'start': self.request.POST.get('start_datetime'),
                'end': self.request.POST.get('end_datetime'),
            }
        return super().form_invalid(form)


class ReservationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Reservation
    template_name = 'reservation/admin_list.html'
    context_object_name = 'reservations'
    paginate_by = 20

    def get_queryset(self):
        return Reservation.objects.filter(status='pending').select_related('user', 'slot__place__coworking').order_by('-created_at')

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('coworkings:list')


class ReservationActionView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk, action):
        reservation = get_object_or_404(Reservation, pk=pk, status='pending')

        if action == 'confirm':
            reservation.status = 'confirmed'
            messages.success(request, f'Заявка #{pk} подтверждена.')
        elif action == 'reject':
            reservation.status = 'rejected'
            messages.warning(request, f'Заявка #{pk} отклонена.')
        else:
            messages.error(request, 'Неизвестное действие.')
            return redirect('reservations:admin_list')

        reservation.save()
        return redirect('reservations:admin_list')

    def test_func(self):
        return self.request.user.is_staff


class CancelReservationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

        # Проверяем, можно ли отменить
        if reservation.status not in ['pending', 'confirmed']:
            messages.error(request, "Эту заявку уже нельзя отменить.")
            return redirect('users:profile')

        if reservation.slot.start_datetime <= timezone.now():
            messages.error(request, "Нельзя отменить заявку, время которой уже прошло.")
            return redirect('users:profile')

        # Отменяем
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, "Заявка отменена.")
        return redirect('users:profile')