"""wat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from wot_banner.views import banner, banner_x_accel
from wot_web_wtr.views import test

urlpatterns = [
    path('auth/', include('wot_user.urls')),
    path('test/', include('wat_test.urls')),
    path('b.jpg', banner),
    path('c.jpg', banner_x_accel),
    path('t', test),
    path('a/', include('wot_admin_tools.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns
