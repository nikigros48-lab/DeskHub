from django.urls import path
from .views import CreateReservationView, ReservationListView, ReservationActionView, CancelReservationView

app_name = 'reservations'


urlpatterns = [
    path('create/', CreateReservationView.as_view(), name='create'),
    path('admin/', ReservationListView.as_view(), name='admin_list'),
    path('admin/action/<int:pk>/<str:action>/', ReservationActionView.as_view(), name='admin_action'),
    path('cancel/<int:pk>/', CancelReservationView.as_view(), name='cancel'),
]