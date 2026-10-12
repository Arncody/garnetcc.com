"""
فیلتر نمایش تاریخ و ساعت: شمسی برای فارسی و میلادی برای انگلیسی (بدون وابستگی خارجی).
استفاده: {{ post.display_date|site_datetime:lang }}
"""
from django import template
from django.utils import timezone
from django.utils.formats import date_format

register = template.Library()

JALALI_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]


def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = (
        355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100)
        + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    )
    jy = -1595 + (33 * (days // 12053))
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
def site_datetime(value, lang="fa"):
    """تاریخ و ساعت (به وقت محلی سایت)؛ فارسی: «۱۱ مهر ۱۴۰۵ · ساعت ۱۴:۳۰»."""
    if not value:
        return ""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    if lang == "en":
        return date_format(value, "j F Y · H:i")
    jy, jm, jd = gregorian_to_jalali(value.year, value.month, value.day)
    return f"{jd} {JALALI_MONTHS[jm - 1]} {jy} · ساعت {value:%H:%M}"


@register.filter
def site_date(value, lang="fa"):
    """فقط تاریخ، برای کارت‌های فشرده."""
    if not value:
        return ""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    if lang == "en":
        return date_format(value, "j F Y")
    jy, jm, jd = gregorian_to_jalali(value.year, value.month, value.day)
    return f"{jd} {JALALI_MONTHS[jm - 1]} {jy}"
