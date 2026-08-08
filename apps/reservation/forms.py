from django import forms
from apps.coworkings.models import Place

class ReservationForm(forms.Form):
    place = forms.ModelChoiceField(queryset=Place.objects.filter(is_blocked=False), label="Выберите место")
    start_datetime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label="Начало")
    end_datetime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label="Конец")
    participants = forms.IntegerField(min_value=1, initial=1, label="Количество участников")

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_datetime')
        end = cleaned_data.get('end_datetime')
        if start and end and start >= end:
            raise forms.ValidationError("Время начала должно быть раньше времени окончания.")
        return cleaned_data