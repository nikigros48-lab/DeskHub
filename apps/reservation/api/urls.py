from django.urls import path
from .views import ReservationStatusView

app_name = 'reservation_api'

urlpatterns = [
    path('<int:pk>/status/', ReservationStatusView.as_view(), name='status'),
]