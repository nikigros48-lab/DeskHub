import profile

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import UpdateView, TemplateView

from apps.reservation.models import Reservation
from apps.users.forms import UserProfileForm
from apps.users.models import Profile


# class ProfileEditView(LoginRequiredMixin, UpdateView):
#     model = Profile
#     form_class = UserProfileForm
#     template_name = 'users/profile_edit.html'
#     success_url = reverse_lazy('users:edit')
#
#     def get_object(self, queryset=None):
#         profile, created = Profile.objects.get_or_create(user=self.request.user)
#         return profile
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user'] = self.request.user
#         return kwargs
#
#     def form_valid(self, form):
#         messages.success(self.request, "Профиль успешно обновлён")
#         return super().form_valid(form)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = self.request.GET.get('tab', 'reservations')
        context['active_tab'] = tab
        profile, created = Profile.objects.get_or_create(user=self.request.user)

        if tab == 'edit':
            context['form'] = UserProfileForm(
                instance=profile,
                user=self.request.user
            )

        elif tab == 'reservations':
            reservations = Reservation.objects.filter(
                user=self.request.user
            ).select_related(
                'slot__place__coworking'
            ).order_by('-created_at')
            context['reservations'] = reservations

        context['now'] = timezone.now()

        return context

    def post(self, request, *args, **kwargs):
        profile, created = Profile.objects.get_or_create(user=request.user)
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлён")
        else:
            messages.error(request, "Исправьте ошибки в форме")
        return redirect(f"{reverse_lazy('users:profile')}?tab=edit")