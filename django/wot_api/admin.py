from django.contrib import admin

from . import models


@admin.register(models.Clan)
class ClanAdmin(admin.ModelAdmin):
    pass
