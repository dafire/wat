from django import template

from ..tasks import convert_timestamp

register = template.Library()


@register.filter
def tsdate(value):
    return convert_timestamp(value)
