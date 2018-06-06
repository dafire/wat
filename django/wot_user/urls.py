from django.urls import path

from . import views

app_name = "wot_user"

urlpatterns = [
    path('login', views.simple_login, name="login"),
    path('login/page', views.login_view, name="login-ext"),
    path('login2', views.ext_login, name="login2"),
    path('callback', views.simple_callback, name="callback"),
    path('callback2', views.ext_callback, name="callback2"),
    path('logout', views.logoutView, name="logout"),
]
