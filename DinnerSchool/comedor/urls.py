from django.urls import path

from . import views

app_name = 'comedor'

urlpatterns = [
    path("ingredients/", views.ingredients, name="ingredients"),
    path("ingredients/create/", views.createIngredient, name="createIngredient"),
    path("saucers/", views.saucers, name="saucers"),
    path("saucers/create/", views.createSaucer, name="createSaucer"),
    path("order/", views.order, name="order"),
    path("credit/", views.credit, name="credit"),
    path("ads/", views.ads, name="ads"),
]