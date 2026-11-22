"""Homepage links configured in the content editor."""

from urllib.parse import urlsplit

from django import template
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

register = template.Library()

LEGACY_PROJECT_ANCHORS = {"#ongoing-projects", "#ongoing", "#showcase", "#completed"}


@register.simple_tag
def home_project_action_url(value, status):
    fallback = f"{reverse('website:projects_list')}#{status}"
    value = (value or "").strip()
    if not value or value in LEGACY_PROJECT_ANCHORS or "\\" in value:
        return fallback
    try:
        parsed = urlsplit(value)
    except ValueError:
        return fallback
    if parsed.netloc and not parsed.scheme:
        return fallback
    if value.startswith("#"):
        return f"{reverse('website:home')}{value}"
    if url_has_allowed_host_and_scheme(value, allowed_hosts={parsed.netloc}):
        return value
    return fallback
