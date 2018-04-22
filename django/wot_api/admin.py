from django.contrib import admin

from . import models


@admin.register(models.Clan)
class ClanAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ClanInfo)
class ClanInfoAdmin(admin.ModelAdmin):
    list_display = ["pk", "account_id", "clan_id", "updated"]

    readonly_fields = list_display + ["account", "clan"]


@admin.register(models.UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ["account", "created"]

    readonly_fields = list_display + ["data"]


@admin.register(models.VehicleStatistic)
class VehicleStatisticAdmin(admin.ModelAdmin):
    list_display = ["account", "created"]
