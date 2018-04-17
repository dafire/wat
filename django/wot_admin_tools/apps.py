from importlib import import_module

from django.apps import AppConfig
from django.conf import settings
from django.conf.urls import url
from django.urls import reverse, NoReverseMatch, include


class WotAdminToolsConfig(AppConfig):
    name = 'wot_admin_tools'

    def ready(self):
        try:
            reverse("%s:index" % self.name)
        except NoReverseMatch:
            urlconf_module = import_module(settings.ROOT_URLCONF)
            urlconf_module.urlpatterns = [url(r'^admin_tools/',
                                              include(self.name + ".urls"))] + urlconf_module.urlpatterns
