from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView
from django.conf.urls.static import static
from booking import settings


urlpatterns = [
    path("", RedirectView.as_view(url="tour_booking/")),
    path("admin/", admin.site.urls),
    path("tour_booking/", include("tour_booking.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)