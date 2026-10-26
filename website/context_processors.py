from .models import SiteSettings, SiteTheme, SiteTexts, CompanyCatalog, MenuItem
from .forms import ConsultationForm
from .theme_tokens import build_theme_css


def _menu_items(request, lang):
    """منوی اصلی از پنل ادمین (به‌همراه زیرمنوها)؛ آیتم فعال بر اساس مسیر فعلی مشخص می‌شود."""
    path = request.path or "/"
    items = []
    for item in MenuItem.objects.filter(is_active=True).prefetch_related("children"):
        url = (item.url or "").strip()
        base = url.split("#", 1)[0]
        has_hash = "#" in url
        if item.open_consult or has_hash or not base:
            active = False
        elif base == "/":
            active = path == "/"
        else:
            active = path.startswith(base)
        children = []
        if not item.open_consult:
            for sub in item.children.all():
                sub_url = (sub.url or "").strip()
                if not sub.is_active or not sub_url:
                    continue
                children.append({
                    "label": (sub.title_en or sub.title) if lang == "en" else sub.title,
                    "url": sub_url,
                })
        items.append({
            "label": (item.title_en or item.title) if lang == "en" else item.title,
            "url": url or "#",
            "base": base,
            "consult": item.open_consult,
            "active": active,
            "children": children,
        })
    return items


def site_settings(request):
    lang = request.session.get("site_lang", "fa")
    if lang not in {"fa", "en"}:
        lang = "fa"
    texts = SiteTexts.load().resolve(lang)
    settings_obj = SiteSettings.load()
    theme = SiteTheme.load()
    return {
        "site_settings": settings_obj,
        "rail_home": settings_obj.projects_carousel_enabled,
        "rail_list": settings_obj.projects_carousel_enabled and settings_obj.projects_carousel_on_list,
        "site_theme": theme,
        "theme_css": build_theme_css(theme.color_overrides),
        "catalog": CompanyCatalog.objects.filter(is_active=True).first(),
        "lang": lang,
        "is_en": lang == "en",
        "T": texts,
        "consultation_form": ConsultationForm(language=lang, texts=texts),
        "menu_items": _menu_items(request, lang),
    }
