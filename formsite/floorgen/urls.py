from django.urls import path

from . import views

app_name = "floorgen"
urlpatterns = [
    path("", views.index, name="index"),
]
