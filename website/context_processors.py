from django.urls import reverse

from .models import SiteSettings, SiteTheme, SiteTexts, CompanyCatalog, MenuItem
from .forms import ConsultationForm
from .navigation import is_legacy_about_link, is_projects_link, is_retired_blog_link
from .theme_tokens import PALETTE, build_theme_css, normalize_color


THEME_COLOR_FIELDS = (
    "background", "surface", "primary", "secondary", "accent", "accent_hover",
    "text", "muted", "white", "dark", "border", "glass", "glass_dark", "overlay",
    "header_background", "header_text", "header_muted", "header_cta_background",
    "header_cta_text", "header_cta_border", "menu_line_color",
    "primary_button_background", "primary_button_text", "primary_button_hover",
    "glass_button_background", "glass_button_border", "modal_background",
    "modal_border", "footer_background", "footer_text",
)


def _theme_color_properties(theme):
    """Publish explicit SiteTheme colors; let the design system supply historical defaults."""
    properties = {}
    for field in THEME_COLOR_FIELDS:
        value = normalize_color(getattr(theme, field))
        default = normalize_color(SiteTheme._meta.get_field(field).get_default())
        if value is not None and value != default:
            properties[field.replace("_", "-")] = value
    return properties


def _menu_items(request, lang, texts):
    path = request.path
    host = request.get_host()
    home_path = reverse("website:home")
    about_path = reverse("website:about")
    projects_path = reverse("website:projects_list")
    items = []
    for item in MenuItem.objects.filter(is_active=True).prefetch_related("children"):
        url = (item.url or "").strip()
        if not item.open_consult and is_retired_blog_link(url, host):
            continue
        if not item.open_consult and is_legacy_about_link(url, host, home_path):
            url = about_path
        base = url.split("#", 1)[0]
        active = not item.open_consult and "#" not in url and bool(base) and (
            path == home_path if base == home_path else path == base or path.startswith(base.rstrip("/") + "/")
        )
        children = []
        if not item.open_consult and is_projects_link(url, host, projects_path, home_path):
            url, active = projects_path, path.startswith(projects_path)
            children = [
                {"label": texts["projects_ongoing_title"], "url": projects_path + "#ongoing"},
                {"label": texts["projects_completed_title"], "url": projects_path + "#completed"},
            ]
        elif not item.open_consult:
            for sub in item.children.all():
                sub_url = (sub.url or "").strip()
                if not sub.is_active or not sub_url or is_retired_blog_link(sub_url, host):
                    continue
                if is_legacy_about_link(sub_url, host, home_path):
                    sub_url = about_path
                children.append({
                    "label": (sub.title_en or sub.title) if lang == "en" else sub.title,
                    "url": sub_url,
                })
        items.append({
            "label": (item.title_en or item.title) if lang == "en" else item.title,
            "url": url or "#",
            "consult": item.open_consult,
            "active": active,
            "children": children,
        })
    return items


def site_copy(request):
    if not hasattr(request, "_garnet_copy"):
        lang = "en" if request.session.get("site_lang") == "en" else "fa"
        request._garnet_copy = (lang, SiteTexts.load().resolve(lang))
    return request._garnet_copy


def site_settings(request):
    lang, texts = site_copy(request)
    settings_obj = SiteSettings.load()
    theme = SiteTheme.load()
    colors = _theme_color_properties(theme)
    return {
        "site_settings": settings_obj,
        "rail_home": settings_obj.projects_carousel_enabled,
        "site_theme": theme,
        "theme_color_properties": colors,
        "theme_background": colors.get("background", PALETTE["off-white"]),
        "theme_palette": PALETTE,
        "theme_css": build_theme_css(theme.color_overrides),
        "catalog": CompanyCatalog.objects.filter(is_active=True).first(),
        "lang": lang,
        "is_en": lang == "en",
        "T": texts,
        "consultation_form": ConsultationForm(language=lang, texts=texts),
        "menu_items": _menu_items(request, lang, texts),
    }
