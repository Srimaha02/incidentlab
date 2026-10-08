from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("scenario/<slug:slug>/", views.scenario, name="scenario"),
]