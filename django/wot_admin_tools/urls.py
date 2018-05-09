from django.urls import path

from . import views

app_name = "wot_admin_tools"

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('task/', views.TaskView.as_view(), name='task-url'),
    path('download/', views.download_backup, name='download-backup'),
]
