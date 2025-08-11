from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path("signInUp/", views.signInUp, name="signInUp"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("bulk_delete/<str:model_name>/<str:redirect_url>/", views.bulk_delete, name="bulk_delete"),
    path("students/", views.students, name="students"),
    path("createStudents/", views.createStudents, name="createStudents"),
    path("employee/", views.employee, name="employee"),
    path("educational/", views.education_level, name="educational"),
    path("users/", views.user_list_view, name="user_list_view"),
    path("account_settings/", views.account_settings_form_view, name="account_settings"),
]