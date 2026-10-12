from pathlib import Path

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from products.images import media_url

register = template.Library()

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


@register.filter
def toman(value):
    return f"{int(value):,}".translate(PERSIAN_DIGITS).replace(",", "٬")


@register.filter
def fa(value):
    return str(value).translate(PERSIAN_DIGITS)


@register.simple_tag
def icon(name):
    path = Path(settings.BASE_DIR) / "static" / "icons" / f"{name}.svg"
    return mark_safe(path.read_text(encoding="utf-8")) if path.is_file() else ""


@register.simple_tag
def banner(name):
    return media_url("banners", name)
