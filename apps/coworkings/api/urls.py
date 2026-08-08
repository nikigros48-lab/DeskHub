from django.urls import path
from .views import CoworkingListView, CoworkingDetailAPIView

app_name = 'coworkings_api'

urlpatterns = [
    path('', CoworkingListView.as_view(), name='list'),
    path('<int:pk>/', CoworkingDetailAPIView.as_view(), name='detail'),
]