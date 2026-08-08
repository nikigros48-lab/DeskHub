# from django.urls import path
#
# from apps.users.views import ProfileEditView
#
# app_name = 'users'
#
# urlpatterns = [
#     path('', ProfileEditView.as_view(), name='edit'),
# ]

from django.urls import path
from .views import ProfileView

app_name = 'users'

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
]