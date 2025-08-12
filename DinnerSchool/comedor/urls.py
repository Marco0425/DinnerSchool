from django.urls import path


from . import views

app_name = 'comedor'

urlpatterns = [
    path("ingredients/", views.ingredients, name="ingredients"),
    path("ingredients/create/", views.createIngredient, name="createIngredient"),
    path("saucers/", views.saucers, name="saucers"),
    path("saucers/create/", views.createSaucer, name="createSaucer"),
    path("order/", views.order, name="order"),
    path("order/create/", views.createOrder, name="createOrder"),
    path("credit/", views.credit, name="credit"),
    path("credit/create/", views.createCredit, name="createCredit"),
    path("ads/", views.ads, name="ads"),
    path("ads/create/", views.createAds, name="createAds"),
    path("order/update-status/", views.update_order_status, name="updateOrderStatus"),
]