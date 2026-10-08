from django.http import JsonResponse
from django.urls import include, path


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health, name="health"),
    path("", include("practice.urls")),
    path("doctor/", include("doctor.urls")),
]
