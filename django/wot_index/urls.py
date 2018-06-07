from django.urls import path

from . import views

app_name = "wot_index"

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('ab', views.TestView.as_view()),
    path('p/<uuid:pk>/', views.PlayerView.as_view(), name='player'),
    path('u/<int:pk>/', views.UserInfoView.as_view(), name='userinfo'),
    path('wn8/<uuid:pk>/', views.WN8View.as_view(), name='wn8'),
]
