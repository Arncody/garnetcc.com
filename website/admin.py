from django.contrib import admin
from django.utils.html import format_html
import csv
from django.http import HttpResponse
from .models import (
    SiteSettings, HeroSection, HeroStat, Project, ProjectImage,
    PhilosophyFeature, SiteSection, ConsultationRequest, CompanyCatalog, BlogPost, SiteTheme, SiteTexts, MenuItem, MenuSubItem, NewsletterSubscriber
)

admin.site.site_header = "پنل مدیریت گارنت | Garnet CMS"
admin.site.site_title = "Garnet Admin"
admin.site.index_title = "مرکز فرمان محتوای سایت گارنت"
admin.site.enable_nav_sidebar = True

from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .theme_tokens import GROUPS, ALL_TOKENS, normalize_color, clean_overrides


class ColorTextInput(forms.TextInput):
    input_type = "color"


def _picker_hex(value):
    """رنگ معتبر را به #rrggbb تبدیل می‌کند (برای انتخابگر رنگ مرورگر)؛ در صورت امکان‌نبودن، مشکی."""
    value = normalize_color(value) or ""
    if value.startswith("#"):
        digits = value[1:]
        if len(digits) == 3:
            digits = "".join(ch * 2 for ch in digits)
        if len(digits) in (6, 8):
            return "#" + digits[:6]
    if value.startswith("rgb"):
        try:
            parts = [int(p) for p in value[value.index("(") + 1:value.index(")")].split(",")[:3]]
            return "#%02x%02x%02x" % tuple(parts)
        except (ValueError, TypeError):
            pass
    return "#000000"


class ColorOverrideWidget(forms.Widget):
    """فیلد رنگ: متن (HEX / rgba) + انتخابگر رنگ + نمونه‌ی زنده + دکمه‌ی بازگشت به پیش‌فرض."""

    def __init__(self, default="", attrs=None):
        super().__init__(attrs)
        self.default = default

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        field_id = attrs.get("id") or "id_" + name
        value = (value or "").strip() if isinstance(value, str) else ""
        shown = normalize_color(value) or self.default
        return format_html(
            '<div class="garnet-color" data-default="{default}">'
            '<span class="garnet-color-swatch" aria-hidden="true"><i style="background:{shown}"></i></span>'
            '<input type="text" name="{name}" id="{id}" value="{value}" class="garnet-color-text vTextField" dir="ltr" '
            'maxlength="40" autocomplete="off" spellcheck="false" placeholder="پیش‌فرض: {default}">'
            '<input type="color" class="garnet-color-picker" value="{picker}" aria-label="انتخاب رنگ" tabindex="-1">'
            '<button type="button" class="garnet-color-reset" title="پاک کردن و بازگشت به رنگ پیش‌فرض">↺ پیش‌فرض</button>'
            '</div>',
            default=self.default, shown=shown, name=name, id=field_id, value=value,
            picker=_picker_hex(value or self.default),
        )

    def value_from_datadict(self, data, files, name):
        return data.get(name, "")


BASE_PALETTE_FIELDS = (
    "background", "surface", "primary", "secondary", "accent", "accent_hover",
    "text", "muted", "white", "dark", "border",
)


class SiteThemeFormBase(forms.ModelForm):
    class Meta:
        model = SiteTheme
        fields = "__all__"
        widgets = {name: ColorTextInput() for name in BASE_PALETTE_FIELDS}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        saved = clean_overrides(getattr(self.instance, "color_overrides", None))
        for token in ALL_TOKENS:
            self.initial[token.field_name] = saved.get(token.key, "")

    def clean(self):
        data = super().clean()
        for field in BASE_PALETTE_FIELDS:
            if field not in self.fields:
                continue
            value = (data.get(field) or "").strip()
            if not (value.startswith("#") and len(value) in (4, 7)):
                self.add_error(field, "کد HEX معتبر مثل #004E72 وارد کنید.")
        overrides = {}
        for token in ALL_TOKENS:
            raw = (data.get(token.field_name) or "").strip()
            if not raw:
                continue
            normalized = normalize_color(raw)
            if not normalized:
                self.add_error(token.field_name, "رنگ معتبر وارد کنید؛ مثل #FF6E42 یا rgba(0,0,0,.5) (برای حذف تغییر، فیلد را خالی بگذارید).")
                continue
            overrides[token.key] = normalized
        self.instance.color_overrides = overrides
        return data


# فیلدهای رنگ جزء‌به‌جزء از روی فهرست مرکزی theme_tokens.py ساخته می‌شوند (افزودن رنگ جدید فقط در همان فایل).
SiteThemeForm = type(SiteThemeFormBase)(
    "SiteThemeForm",
    (SiteThemeFormBase,),
    {
        "__module__": __name__,
        **{token.field_name: forms.CharField(
            label=token.label, required=False, max_length=40,
            widget=ColorOverrideWidget(default=token.default),
        )
        for token in ALL_TOKENS},
    },
)


@admin.register(SiteTheme)
class SiteThemeAdmin(admin.ModelAdmin):
    form = SiteThemeForm
    base_fieldsets = (
        ("🎨 رنگ‌های پایه سایت (پالت اصلی)", {"classes": ("collapse",), "fields": (("background", "surface"), ("primary", "secondary"), ("accent", "accent_hover"), ("text", "muted"), ("white", "dark"), ("border",))}),
        ("🪟 شیشه، شفافیت و عمق", {"classes": ("collapse",), "fields": ("glass", "glass_dark", "overlay", "shadow", ("radius", "glass_blur"))}),
        ("● دکمه‌های اصلی (نارنجی) و شیشه‌ای", {"classes": ("collapse",), "fields": (("primary_button_background", "primary_button_text"), ("primary_button_hover",), ("glass_button_background", "glass_button_border"))}),
        ("▤ پوشش روی تصویر Hero", {"classes": ("collapse",), "fields": (("hero_overlay",),)}),
        ("🖼️ اندازه لوگو", {"classes": ("collapse",), "fields": (("logo_width_desktop", "logo_width_mobile"),)}),
        ("Aa تایپوگرافی و وزن فونت", {"classes": ("collapse",), "fields": (("body_weight", "heading_weight"), ("hero_weight", "section_weight"), ("card_weight", "nav_weight"), ("button_weight", "label_weight"), ("small_weight",)), "description": "وزن‌های قابل استفاده فونت IranSans: 300، 400، 500، 600 و 700."}),
        ("⚙️ سفارشی‌سازی پیشرفته", {"classes": ("collapse",), "fields": ("custom_css",)}),
    )

    def get_fieldsets(self, request, obj=None):
        component_sets = []
        for index, group in enumerate(GROUPS):
            description = group.description
            if index == 0:
                description = (
                    "راهنما: برای هر بخش سایت می‌توانید رنگ را جداگانه تغییر دهید. در هر ردیف یا کد رنگ را بنویسید "
                    "(مثل #000000 یا rgba(0,0,0,.5) برای شفافیت) یا از مربع رنگ انتخاب کنید. "
                    "فیلد خالی = رنگ پیش‌فرض سایت؛ دکمه «پیش‌فرض» هر ردیف تغییر را برمی‌گرداند. "
                    "بعد از ذخیره، سایت را یک‌بار با Ctrl+F5 باز کنید. — " + group.description
                )
            component_sets.append((
                group.title,
                {"fields": [token.field_name for token in group.tokens], "description": description,
                 **({} if index == 0 else {"classes": ("collapse",)})},
            ))
        return tuple(component_sets) + self.base_fieldsets

    class Media:
        css = {"all": ("css/admin-theme-colors.css",)}
        js = ("js/admin-theme-colors.js",)

    def has_add_permission(self, request):
        return not SiteTheme.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets=(
        ("برند / Brand",{"fields":("brand_name","legal_name","logo","logo_light","favicon",("tagline","tagline_en"))}),
        ("تماس / Contact",{"fields":("phone","email","address","instagram_url","linkedin_url")}),
        ("چرخش پروژه‌ها / Projects carousel",{"fields":("projects_carousel_enabled","projects_carousel_speed")}),
        ("رزرو / Booking",{"fields":("booking_url","working_hours_weekday","working_hours_weekend")}),
        ("SEO",{"fields":("meta_title","meta_description")}),
    )
    def has_add_permission(self,request): return not SiteSettings.objects.exists()
    def has_delete_permission(self,request,obj=None): return False

class HeroStatInline(admin.TabularInline):
    model=HeroStat; extra=1; max_num=8; fields=("value","label","label_en","order")

@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    fieldsets=(
        ("فارسی",{"fields":("title","subtitle")}),
        ("English",{"fields":("title_en","subtitle_en")}),
        ("تصویر / ویدیو / Media",{"fields":("background_image","background_video")}),
        ("CTA فارسی",{"fields":(("primary_button_text","primary_button_url"),("secondary_button_text","secondary_button_url"),("tertiary_button_text","tertiary_button_url"))}),
        ("CTA English",{"fields":(("primary_button_text_en",),("secondary_button_text_en",),("tertiary_button_text_en",))}),
    ); inlines=[HeroStatInline]
    def has_add_permission(self,request): return not HeroSection.objects.exists()
    def has_delete_permission(self,request,obj=None): return False

class ProjectImageInline(admin.TabularInline):
    model=ProjectImage; extra=1; fields=("image","preview","category","caption","caption_en","description","description_en","order"); readonly_fields=("preview",)
    def preview(self,obj): return format_html('<img src="{}" style="height:60px;border-radius:8px;object-fit:cover"/>',obj.image.url) if obj.image else "—"

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display=("title","title_en","status","location","year","is_featured","is_active","order"); list_editable=("is_featured","is_active","order"); list_filter=("status","is_active","is_featured"); search_fields=("title","title_en","code","location","location_en"); prepopulated_fields={"slug":("title",)}; ordering=("order",); inlines=[ProjectImageInline]
    fieldsets=(("فارسی",{"fields":("title","code","slug","status","status_note","location","year","short_description","full_description","feature_list","badge_text","cta_text")}), ("English",{"fields":("title_en","status_note_en","location_en","short_description_en","full_description_en","feature_list_en","badge_text_en","cta_text_en")}), ("تصویر و نمایش",{"fields":("main_image","is_featured","is_active","order")}), ("سیستمی",{"fields":("created_at",)})); readonly_fields=("created_at",)

@admin.register(PhilosophyFeature)
class PhilosophyFeatureAdmin(admin.ModelAdmin):
    list_display=("title","title_en","order","is_active"); list_editable=("order","is_active"); search_fields=("title","title_en","description","description_en"); ordering=("order",)
    fieldsets=(("فارسی",{"fields":("icon_glyph","title","description")}), ("English",{"fields":("title_en","description_en")}), ("نمایش",{"fields":("order","is_active")}))

@admin.register(SiteSection)
class SiteSectionAdmin(admin.ModelAdmin):
    list_display=("key","title","title_en","is_active","order"); list_editable=("is_active","order"); list_filter=("is_active",); search_fields=("title","title_en","content","content_en")
    fieldsets=(("شناسه",{"fields":("key",)}),("فارسی",{"fields":("title","subtitle","content","quote_text","quote_author")}), ("English",{"fields":("title_en","subtitle_en","content_en","quote_text_en","quote_author_en")}), ("تصویر / نمایش",{"fields":("image","is_active","order")}))

@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display=("name","gender","phone","subject","status","created_at"); list_editable=("status",); list_filter=("gender","status","created_at"); search_fields=("name","phone","subject"); readonly_fields=("name","gender","phone","subject","message","created_at","ip_address"); ordering=("-created_at",)
    def has_add_permission(self,request): return False


@admin.register(CompanyCatalog)
class CompanyCatalogAdmin(admin.ModelAdmin):
    list_display = ("title", "title_en", "is_active", "updated_at")
    list_editable = ("is_active",)
    search_fields = ("title", "title_en")
    fieldsets = (
        ("کاتالوگ", {"fields": ("title", "title_en", "file", "is_active")}),
    )


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "title_en", "category", "is_published", "is_featured", "published_at")
    list_editable = ("is_published", "is_featured")
    list_filter = ("is_published", "is_featured", "category")
    search_fields = ("title", "title_en", "excerpt", "excerpt_en", "content", "content_en", "seo_title", "seo_title_en")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("فارسی", {"fields": ("title", "slug", "excerpt", "content", "category")}),
        ("English", {"fields": ("title_en", "excerpt_en", "content_en", "category_en")}),
        ("تصویر و انتشار", {"fields": ("cover", "is_published", "is_featured", "published_at"), "description": "زمان انتشار در سایت (تاریخ و ساعت) زیر عنوان مقاله نمایش داده می‌شود."}),
        ("SEO", {"fields": ("seo_title", "seo_title_en", "seo_description", "seo_description_en")}),
    )


@admin.register(SiteTexts)
class SiteTextsAdmin(admin.ModelAdmin):
    """ویرایش عنوان‌های صفحه اصلی، کادر مشاوره و تمام متن‌های فرم درخواست (فارسی + انگلیسی)."""
    fieldsets = (
        ("🔘 دکمه‌ی آیکونی «مشاهده همه پروژه‌ها» (صفحه اصلی)", {"fields": (("all_projects_btn","all_projects_btn_en"),), "description": "دکمه فقط آیکون دارد؛ این متن برای راهنمای شناور (tooltip) و دسترس‌پذیری استفاده می‌شود."}),
        ("📰 بخش بلاگ (صفحه اصلی)", {"fields": (("journal_title","journal_title_en"),("all_articles_link","all_articles_link_en"),)}),
        ("📚 صفحه «همه مقالات»", {"fields": (("blog_page_title","blog_page_title_en"),)}),
        ("📞 عنوان دکمه‌های درخواست مشاوره", {"fields": (("consultation_button_text", "consultation_button_text_en"), ("cta_button", "cta_button_en"))}),
        ("📝 پاپ‌آپ فرم درخواست مشاوره", {"fields": (("modal_title","modal_title_en"),("modal_subtitle","modal_subtitle_en"),("submit_text","submit_text_en"),)}),
        ("🏷️ عنوان فیلدهای فرم", {"fields": (("label_name","label_name_en"),("label_gender","label_gender_en"),("label_phone","label_phone_en"),("label_subject","label_subject_en"),("label_message","label_message_en"),)}),
        ("✍️ متن راهنمای داخل فیلدها (Placeholder)", {"fields": (("ph_name","ph_name_en"),("ph_phone","ph_phone_en"),("ph_subject","ph_subject_en"),("ph_message","ph_message_en"),)}),
        ("👤 گزینه‌های فیلد «عنوان»", {"fields": (("opt_male","opt_male_en"),("opt_female","opt_female_en"),("opt_other","opt_other_en"),)}),
    )

    def has_add_permission(self, request):
        return not SiteTexts.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class MenuSubItemInline(admin.TabularInline):
    model = MenuSubItem
    extra = 0
    fields = ("title", "title_en", "url", "order", "is_active")
    verbose_name = "زیرمنو"
    verbose_name_plural = "زیرمنوها (با کلیک روی آیتم، این گزینه‌ها باز می‌شوند)"


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """منوی اصلی سایت (هدر دسکتاپ + منوی موبایل): افزودن، حذف، تغییر عنوان/لینک و ترتیب."""
    list_display = ("title", "title_en", "url", "open_consult", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "open_consult")
    search_fields = ("title", "title_en", "url")
    ordering = ("order", "id")
    inlines = [MenuSubItemInline]
    fieldsets = (
        ("آیتم منو", {"fields": (("title", "title_en"), "url", "open_consult", ("order", "is_active"))}),
    )


def export_active_newsletter_emails(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="garnet-newsletter-subscribers.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(["email", "subscribed_at", "active"])
    for subscriber in queryset.order_by("-created_at"):
        writer.writerow([subscriber.email, subscriber.created_at.isoformat(), subscriber.is_active])
    return response
export_active_newsletter_emails.short_description = "خروجی CSV ایمیل‌های انتخاب‌شده"


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("email",)
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
    fields = ("email", "is_active", "created_at", "updated_at")
    actions = (export_active_newsletter_emails,)
