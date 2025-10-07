from django.urls import path


from . import views

app_name = 'comedor'

urlpatterns = [
    path("ingredients/", views.ingredients, name="ingredients"),
    path('kanban/orders/', views.kanban_orders_api, name='kanban_orders_api'),
    path("ingredients/create/", views.createIngredient, name="createIngredient"),
    path("saucers/", views.saucers, name="saucers"),
    path("saucers/create/", views.createSaucer, name="createSaucer"),
    path("order/", views.order, name="order"),
    path("order/history/", views.orderHistory, name="orderHistory"),
    path("order/create/", views.createOrder, name="createOrder"),
    path("credit/", views.credit, name="credit"),
    path("credit/create/", views.createCredit, name="createCredit"),
    path("ads/", views.ads, name="ads"),
    path("ads/create/", views.createAds, name="createAds"),
    path("order/update-status/", views.update_order_status, name="updateOrderStatus"),
    path("credit/report/generate/", views.generarReporte, name="generarReporte"),
    path("cancelOrder/<int:pedido_id>/", views.cancelOrder, name="cancelOrder"),
    path('order/<int:order_id>/details/', views.order_details_api, name='order_details_api'),
    path('order/<int:order_id>/modify/', views.modify_order_view, name='modify_order'),
    path('accountStatements/', views.accountStatements, name='accountStatements'),
    path('get-movimientos/', views.get_movimientos, name='get_movimientos'),
]