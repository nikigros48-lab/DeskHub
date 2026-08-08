from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from apps.coworkings.models import Slot


class Reservation(models.Model):
    STATUS_CHOICES = (
        ("pending", "Ожидает"),
        ("confirmed", "Подтверждена"),
        ("rejected", "Отклонена"),
        ("cancelled", "Отменена"),
        ("completed", "Завершена"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='reservations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'reservation'
        ordering = ['-created_at']
        unique_together = (('user', 'slot'),)
        verbose_name_plural = verbose_name = 'Бронь'

    def __str__(self):
        return f"{self.user.username} | {self.slot} | {self.get_status_display()}"

    def clean(self):
        if self.status == 'confirmed':
            conflicting = Reservation.objects.filter(
                slot=self.slot,
                status='confirmed'
            ).exclude(pk=self.pk)
            if conflicting.exists():
                raise ValidationError("Этот слот уже забронирован другим пользователем.")
