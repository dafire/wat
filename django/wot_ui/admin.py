from django.contrib import admin
from django.db import models

from simplemde.widgets import SimpleMDETextarea
from . import models as m


@admin.register(m.Page)
class PageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': SimpleMDETextarea},
    }

    class Media:
        css = {
            'all': ('simplemde/simplemde.min.css',)
        }
        js = ('simplemde/simplemde.min.js',)
