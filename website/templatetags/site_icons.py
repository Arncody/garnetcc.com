"""
آیکون‌های SVG خطی (inline) برای سراسر سایت؛ بدون فایل یا کتابخانه‌ی خارجی.
استفاده در قالب:  {% load site_icons %}  {% icon "phone" %}  یا  {% icon "phone" 20 %}
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_PATHS = {
    "phone": '<path d="M5 4h3.2l1.6 4-2 1.3a11 11 0 0 0 5.9 5.9l1.3-2 4 1.6V18a2 2 0 0 1-2.2 2A15 15 0 0 1 3 6.2 2 2 0 0 1 5 4z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7.5 8 6 8-6"/>',
    "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none"/>',
    "linkedin": '<rect x="3.5" y="3.5" width="17" height="17" rx="3.5"/><path d="M8 10.5V16M8 7.8v.1M11.5 16v-3.2a2.3 2.3 0 0 1 4.6 0V16M11.5 10.5V16"/>',
    "pin": '<path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 1 1 13 0C18.5 15.4 12 21 12 21z"/><circle cx="12" cy="10" r="2.3"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "building": '<path d="M5 20V5.5A1.5 1.5 0 0 1 6.5 4h7A1.5 1.5 0 0 1 15 5.5V20M15 9h2.5A1.5 1.5 0 0 1 19 10.5V20M3.5 20h17M8.5 8h3M8.5 12h3M8.5 16h3"/>',
    "check-building": '<path d="M5 20V5.5A1.5 1.5 0 0 1 6.5 4h7A1.5 1.5 0 0 1 15 5.5V20M3.5 20h17M8.5 8h3M8.5 12h3"/><path d="m16.5 14.5 1.8 1.8 3.2-3.6"/>',
    "book": '<path d="M5 5.5A1.5 1.5 0 0 1 6.5 4H19v13H6.5A1.5 1.5 0 0 0 5 18.5v-13zM5 18.5A1.5 1.5 0 0 0 6.5 20H19v-3"/><path d="M9 8h6"/>',
    "download": '<path d="M12 4v11m0 0-4-4m4 4 4-4M5 19h14"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "message": '<path d="M5 5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-7l-4.5 3.5V17H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z"/><path d="M8 10h8M8 13h5"/>',
    "arrow-left": '<path d="M19 12H5m6-6-6 6 6 6"/>',
    "arrow-right": '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    "arrow-up-right": '<path d="M7 17 17 7M8 7h9v9"/>',
    "arrow-up": '<path d="M12 19V5m-6 6 6-6 6 6"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.6 2.6 14.4 0 17M12 3.5c-2.6 2.6-2.6 14.4 0 17"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "wrench": '<path d="M14.5 6.5a4 4 0 0 0 5 5l-9.2 9.2a2.1 2.1 0 0 1-3-3L16.5 8.5"/><path d="M14.5 6.5 17 4l3 3-2.5 2.5"/>',
}

_ALIASES = {"hours": "clock", "location": "pin", "email": "mail", "tel": "phone", "ongoing": "wrench",
            "completed": "check-building", "blog": "book", "consult": "message", "catalog": "download"}


@register.simple_tag
def icon(name, size=18):
    """یک آیکون SVG خطی با اندازه‌ی دلخواه برمی‌گرداند (رنگ از currentColor)."""
    key = _ALIASES.get(name, name)
    body = _PATHS.get(key)
    if body is None:
        return ""
    try:
        size = int(size)
    except (TypeError, ValueError):
        size = 18
    return mark_safe(
        f'<svg class="ic ic-{key}" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
        f'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true" focusable="false">{body}</svg>'
    )
