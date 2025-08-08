from django.urls import path

from . import views

app_name = 'comedor'

urlpatterns = [
    path("ingredients/", views.ingredients, name="ingredients"),
    path("saucers/", views.saucers, name="saucers"),
    path("order/", views.order, name="order"),
    path("credit/", views.credit, name="credit"),
    path("ads/", views.ads, name="ads"),
]