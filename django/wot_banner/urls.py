from django.urls import path

from . import views

app_name = "wot_banner"

urlpatterns = [
    path('banner/<int:userid>.png', views.banner_view, name="banner"),
    path('banner/<int:userid>/', views.banner_view_adhoc, name="adhoc"),
    path('banner/search', views.banner_search_view),
    path('b.jpg', views.banner),
    path('c.jpg', views.banner_x_accel),
]
