from .models import SiteSettings, SiteTheme, SiteTexts, CompanyCatalog, MenuItem
from .forms import ConsultationForm


def _menu_items(request, lang):
    """منوی اصلی از پنل ادمین؛ آیتم فعال بر اساس مسیر فعلی مشخص می‌شود."""
    path = request.path or "/"
    items = []
    for item in MenuItem.objects.filter(is_active=True):
        url = (item.url or "").strip()
        base = url.split("#", 1)[0]
        has_hash = "#" in url
        if item.open_consult or has_hash or not base:
            active = False
        elif base == "/":
            active = path == "/"
        else:
            active = path.startswith(base)
        items.append({
            "label": (item.title_en or item.title) if lang == "en" else item.title,
            "url": url or "#",
            "consult": item.open_consult,
            "active": active,
        })
    return items


def site_settings(request):
    lang = request.session.get("site_lang", "fa")
    if lang not in {"fa", "en"}:
        lang = "fa"
    texts = SiteTexts.load().resolve(lang)
    settings_obj = SiteSettings.load()
    return {
        "site_settings": settings_obj,
        "rail_home": settings_obj.projects_carousel_enabled,
        "rail_list": settings_obj.projects_carousel_enabled and settings_obj.projects_carousel_on_list,
        "site_theme": SiteTheme.load(),
        "catalog": CompanyCatalog.objects.filter(is_active=True).first(),
        "lang": lang,
        "is_en": lang == "en",
        "T": texts,
        "consultation_form": ConsultationForm(language=lang, texts=texts),
        "menu_items": _menu_items(request, lang),
    }
