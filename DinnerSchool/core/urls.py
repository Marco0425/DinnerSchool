from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path("", views.index, name="index"),
    path("signInUp/", views.signInUp, name="signInUp"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("ingredients/", views.ingredients, name="ingredients"),
]