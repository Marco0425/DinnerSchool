from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path("", views.index, name="index"),
    path("signInUp/", views.signInUp, name="signInUp"),
    path("dashboard/", views.dashboard, name="dashboard"),
]