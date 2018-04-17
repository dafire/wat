from django.urls import path

from . import views

app_name = "wat_user"

urlpatterns = [
    path('login', views.simple_login, name="login"),
    path('login2', views.ext_login, name="login2"),
    path('callback', views.simple_callback, name="callback"),
    path('callback2', views.ext_callback, name="callback2"),
    path('logout', views.logoutView, name="logout"),
]
