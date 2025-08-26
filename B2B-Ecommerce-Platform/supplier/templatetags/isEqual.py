from django import template

register = template.Library()


@register.filter
def isEqual(a, b):
    return True if int(a) == int(b) else False
