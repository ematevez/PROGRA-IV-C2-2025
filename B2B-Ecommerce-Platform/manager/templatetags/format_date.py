from django import template
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils.translation import get_language, activate, gettext

register = template.Library()


@register.filter(name="format_date")
def format_date(a):
    current_language = get_language()
    result = naturalday(a)
    activate(current_language)
    text = gettext(result)
    return text
