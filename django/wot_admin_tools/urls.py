from django.urls import path

from . import views

app_name = "wot_admin_tools"

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
]
