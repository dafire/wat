from django.contrib import admin
from django.contrib.auth.models import Group

from . import models

admin.site.unregister(Group)


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    pass

