from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from apps.coworkings.models import Place, Slot
from apps.reservation.models import Reservation


class CartView(View):
    template_name = 'cart/cart.html'

    def get(self, request):
        cart = request.session.get('cart', [])
        items = []
        for idx, item in enumerate(cart):
            place = get_object_or_404(Place, id=item['place'])
            items.append({
                'place': place,
                'start': item['start'],
                'end': item['end'],
                'participants': item.get('participants', 1),
                'index': idx,
            })
        return render(request, self.template_name, {'items': items})


class AddToCartView(View):
    def post(self, request):
        place_id = request.POST.get('place')
        start = request.POST.get('start_datetime')
        end = request.POST.get('end_datetime')
        participants = request.POST.get('participants', 1)

        if not place_id or not start or not end:
            messages.error(request, 'Заполните все поля')
            return redirect('coworkings:list')

        place = get_object_or_404(Place, id=place_id)

        try:
            participants = int(participants)
        except ValueError:
            participants = 1

        if participants > place.capacity:
            messages.error(request, f'Вместимость места — {place.capacity} человек')
            return redirect('coworkings:detail', pk=place.coworking.id)

        cart = request.session.get('cart', [])
        for item in cart:
            if (item['place'] == int(place_id) and
                item['start'] == start and
                item['end'] == end):
                messages.warning(request, 'Этот слот уже в корзине')
                return redirect('coworkings:detail', pk=place.coworking.id)

        cart.append({
            'place': int(place_id),
            'start': start,
            'end': end,
            'participants': participants,
        })
        request.session['cart'] = cart
        messages.success(request, 'Слот добавлен в корзину')
        return redirect('coworkings:detail', pk=place.coworking.id)


class RemoveFromCartView(View):
    def post(self, request, index):
        cart = request.session.get('cart', [])
        if 0 <= index < len(cart):
            cart.pop(index)
            request.session['cart'] = cart
            messages.success(request, 'Элемент удалён из корзины')
        else:
            messages.error(request, 'Элемент не найден')
        return redirect('cart:view')


class CheckoutView(LoginRequiredMixin, View):
    def post(self, request):
        cart = request.session.get('cart', [])
        if not cart:
            messages.error(request, 'Корзина пуста')
            return redirect('cart:view')

        errors = []
        items_to_create = []

        for item in cart:
            place = get_object_or_404(Place, id=item['place'])
            start = datetime.fromisoformat(item['start'])
            end = datetime.fromisoformat(item['end'])
            participants = item.get('participants', 1)

            if participants > place.capacity:
                errors.append(f"Место {place.place_number} не вмещает {participants} человек")
                continue

            conflicting = Reservation.objects.filter(
                slot__place=place,
                slot__start_datetime__lt=end,
                slot__end_datetime__gt=start,
                status__in=['confirmed', 'pending']
            )
            if conflicting.exists():
                errors.append(f"Время с {start.strftime('%d.%m %H:%M')} по {end.strftime('%H:%M')} на месте {place.place_number} уже занято")
                continue

            items_to_create.append((place, start, end, participants))

        if errors:
            for err in errors:
                messages.error(request, err)
            return redirect('cart:view')

        with transaction.atomic():
            for place, start, end, participants in items_to_create:
                slot = Slot.objects.create(
                    place=place,
                    start_datetime=start,
                    end_datetime=end
                )
                Reservation.objects.create(
                    user=request.user,
                    slot=slot,
                    status='pending'
                )

        request.session['cart'] = []
        messages.success(request, 'Все бронирования созданы! Ожидайте подтверждения.')
        return redirect('users:profile')