from django.urls import path
from .views import CartView, AddToCartView, RemoveFromCartView, CheckoutView

app_name = 'cart'

urlpatterns = [
    path('', CartView.as_view(), name='view'),
    path('add/', AddToCartView.as_view(), name='add'),
    path('remove/<int:index>/', RemoveFromCartView.as_view(), name='remove'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]