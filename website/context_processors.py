from urllib.parse import urlsplit

from django.urls import reverse

from .models import SiteSettings, SiteTheme, SiteTexts, CompanyCatalog, MenuItem
from .forms import ConsultationForm
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


def _menu_items(request, lang, show_journal):
    """منوی اصلی از پنل ادمین (به‌همراه زیرمنوها)؛ آیتم فعال بر اساس مسیر فعلی مشخص می‌شود."""
    path = request.path or "/"
    journal_path = reverse("website:blog_list").rstrip("/")
    home_path = reverse("website:home").strip("/")
    site_host = urlsplit(f"//{request.get_host()}").hostname.removeprefix("www.")

    def is_hidden_journal(url):
        if show_journal:
            return False
        try:
            parsed = urlsplit(url)
            host = (parsed.hostname or "").removeprefix("www.")
        except ValueError:
            return False
        target = parsed.path.strip("/")
        return host in {"", site_host} and (
            "/" + target == journal_path or (target == home_path and parsed.fragment == "blog")
        )

    items = []
    for item in MenuItem.objects.filter(is_active=True).prefetch_related("children"):
        url = (item.url or "").strip()
        if not item.open_consult and is_hidden_journal(url):
            continue
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
                if not sub.is_active or is_hidden_journal(sub_url):
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
                    {"label": "Completed projects" if lang == "en" else "پروژه‌های تکمیل شده", "url": "/projects/#completed"},
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
    colors = _theme_color_properties(theme)
    return {
        "site_settings": settings_obj,
        "rail_home": settings_obj.projects_carousel_enabled,
        "rail_list": settings_obj.projects_carousel_enabled and settings_obj.projects_carousel_on_list,
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
        "menu_items": _menu_items(request, lang, settings_obj.show_journal_in_header),
    }
