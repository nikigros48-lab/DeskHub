from django.urls import path

from apps.coworkings.views import CoworkingListView, CoworkingDetailView, get_slots_partial

app_name = 'coworkings'

urlpatterns = [
    path('', CoworkingListView.as_view(), name='list'),
    path('<int:pk>/', CoworkingDetailView.as_view(), name='detail'),
    path('<int:pk>/slots-partial/', get_slots_partial, name='slots_partial'),
]