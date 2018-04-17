from django.urls import path

from . import views

app_name = "wat_test"

urlpatterns = [
    path('', views.index, name="index"),
    path('components/<str:template_name>.html', views.component)
]
