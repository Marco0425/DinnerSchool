from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path("", views.index, name="index"),
    path("signInUp/", views.signInUp, name="signInUp"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("ingredients/", views.ingredients, name="ingredients"),
    path("ingredients/bulk_delete/", views.ingredients_bulk_delete, name="ingredients_bulk_delete"),
    path("students/", views.students, name="students"),
    path("saucers/", views.saucers, name="saucers"),
    path("order/", views.order, name="order"),
    path("employee/", views.employee, name="employee"),
    path("credit/", views.credit, name="credit"),
    path("educational/", views.education_level, name="educational"),
    path("ads/", views.ads, name="ads"),
    path("users/", views.user_list_view, name="users"),
]