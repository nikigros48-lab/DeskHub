from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.info.urls'), name='info'),
    path('profile/', include('apps.users.urls'), name='profile'),
    path("auth/", include("apps.registration.urls"), name="auth"),
    path("coworkings/", include("apps.coworkings.urls"), name="coworkings"),
    path('reservations/', include('apps.reservation.urls'), name='reservations'),
    path('cart/', include('apps.cart.urls')),

    # API
    path('api/coworkings/', include('apps.coworkings.api.urls')),
    path('api/reservations/', include('apps.reservation.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)