from django.apps import AppConfig
from django.conf import settings
from django.urls import include, path, NoReverseMatch, reverse
from importlib import import_module


class WotIndexConfig(AppConfig):
    name = 'wot_index'

    def ready(self):
        try:
            reverse("%s:index" % self.name)
        except NoReverseMatch:
            print("ADD")
            urlconf_module = import_module(settings.ROOT_URLCONF)
            urlconf_module.urlpatterns = [path('', include(self.name + ".urls"))] + urlconf_module.urlpatterns
