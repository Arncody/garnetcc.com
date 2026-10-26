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
        # زیرمنوی پروژه‌ها را به مسیرهای قطعی وصل می‌کنیم؛ لینک‌های قدیمی مثل #ongoing
        # نباید کاربر را به سکشن هم‌نام در صفحه اصلی بفرستند.
        is_projects_item = (base.rstrip("/").endswith("projects") or "پروژه" in item.title or "project" in (item.title_en or "").lower())
        if not item.open_consult:
            for sub in item.children.all():
                sub_url = (sub.url or "").strip()
                if not sub.is_active:
                    continue
                if is_projects_item:
                    label_probe = f"{sub.title} {sub.title_en}".lower()
                    if any(word in label_probe for word in ("در حال اجرا", "ongoing", "progress")):
                        sub_url = "/projects/#ongoing"
                    elif any(word in label_probe for word in ("تمام", "اتمام", "completed", "finished", "built")):
                        sub_url = "/projects/#completed"
                if not sub_url:
                    continue
                children.append({
                    "label": (sub.title_en or sub.title) if lang == "en" else sub.title,
                    "url": sub_url,
                })
            # منوی پروژه‌ها همیشه دقیقاً دو گزینه استاندارد و با مقصد معتبر دارد؛
            # این کار خطاهای ناشی از لینک ناقص/قدیمی زیرمنو در دیتابیس را خنثی می‌کند.
            if is_projects_item:
                children = [
                    {"label": "Ongoing projects" if lang == "en" else "پروژه‌های در حال اجرا", "url": "/projects/#ongoing"},
                    {"label": "Completed projects" if lang == "en" else "پروژه‌های تمام‌شده", "url": "/projects/#completed"},
                ]
        # لینک والد پروژه‌ها همیشه به صفحه واقعی پروژه‌ها می‌رود؛ حتی اگر مقدار قدیمی
        # دیتابیس خالی یا به یک anchor صفحه اصلی اشاره کند.
        if is_projects_item:
            url = "/projects/"
            base = "/projects/"
            active = path.startswith("/projects/")

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
