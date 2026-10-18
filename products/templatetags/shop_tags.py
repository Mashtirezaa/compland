from pathlib import Path

from django import template
from django.conf import settings
from django.utils import timezone
from django.utils.safestring import mark_safe

from products.images import media_url

register = template.Library()

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def _to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy + 1 if gm > 2 else gy
    days = 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30
    return jy, jm, jd


@register.filter
def toman(value):
    return f"{int(value):,}".translate(PERSIAN_DIGITS).replace(",", "٬")


@register.filter
def fa(value):
    return str(value).translate(PERSIAN_DIGITS)


@register.filter
def shamsi(value):
    if not value:
        return ""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    jy, jm, jd = _to_jalali(value.year, value.month, value.day)
    text = f"{jy:04d}/{jm:02d}/{jd:02d} {value.hour:02d}:{value.minute:02d}"
    return text.translate(PERSIAN_DIGITS)


@register.simple_tag
def icon(name):
    path = Path(settings.BASE_DIR) / "static" / "icons" / f"{name}.svg"
    return mark_safe(path.read_text(encoding="utf-8")) if path.is_file() else ""


@register.simple_tag
def banner(name):
    return media_url("banners", name)
