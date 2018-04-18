from django.urls import path

from . import views

app_name = "wot_index"

urlpatterns = [
    path('', views.ClanView.as_view(), name="index"),
    path('p/<uuid:pk>/', views.PlayerView.as_view(), name='player')
]
