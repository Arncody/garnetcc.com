import csv

from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    SiteSettings, HeroSection, Project, ProjectImage,
    PhilosophyFeature, SiteSection, ConsultationRequest, CompanyCatalog, SiteTheme, SiteTexts, MenuItem, MenuSubItem, NewsletterSubscriber
)
from .interface_copy import COPY_GROUPS
from .navigation import is_retired_blog_link

admin.site.site_header = "پنل مدیریت گارنت | Garnet CMS"
admin.site.site_title = "Garnet Admin"
admin.site.index_title = "مرکز فرمان محتوای سایت گارنت"
admin.site.enable_nav_sidebar = True

from .theme_tokens import (
    ACTIVE_TOKENS, GROUPS, RETIRED_DECORATIONS, PixelToken, clean_overrides, normalize_color,
)


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
            'maxlength="40" autocomplete="off" spellcheck="false" placeholder="پیش‌فرض: {default}" {disabled}>'
            '<input type="color" class="garnet-color-picker" value="{picker}" aria-label="انتخاب رنگ" tabindex="-1" {disabled}>'
            '<button type="button" class="garnet-color-reset" title="پاک کردن و بازگشت به رنگ پیش‌فرض" {disabled}>↺ پیش‌فرض</button>'
            '</div>',
            default=self.default, shown=shown, name=name, id=field_id, value=value,
            picker=_picker_hex(value or self.default),
            disabled="disabled" if attrs.get("disabled") else "",
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
        for token in ACTIVE_TOKENS:
            self.initial[token.field_name] = saved.get(token.key, "")

    def clean(self):
        data = super().clean()
        for field in BASE_PALETTE_FIELDS:
            if field not in self.fields:
                continue
            value = (data.get(field) or "").strip()
            if not (value.startswith("#") and len(value) in (4, 7) and normalize_color(value)):
                self.add_error(field, "کد HEX معتبر مثل #004E72 وارد کنید.")
        stored = self.instance.color_overrides
        overrides = dict(stored) if isinstance(stored, dict) else {}
        for token in ACTIVE_TOKENS:
            if token.field_name not in data:
                continue
            raw = data[token.field_name]
            if raw in (None, ""):
                overrides.pop(token.key, None)
                continue
            normalized = token.normalize(raw)
            if normalized is None:
                self.add_error(token.field_name, "رنگ معتبر وارد کنید؛ مثل #141414، rgba(0,0,0,.5) یا transparent.")
                continue
            overrides[token.key] = normalized
        self.instance.color_overrides = overrides
        return data


def theme_override_field(token):
    if isinstance(token, PixelToken):
        return forms.IntegerField(
            label=token.label, required=False, min_value=token.minimum, max_value=token.maximum,
            widget=forms.NumberInput(attrs={"placeholder": f"پیش‌فرض: {token.default}"}),
            help_text=f"پیش‌فرض {token.default} پیکسل، محدودهٔ مجاز {token.minimum} تا {token.maximum} پیکسل.",
        )
    return forms.CharField(
        label=token.label, required=False, max_length=40,
        widget=ColorOverrideWidget(default=token.default),
    )


# تنظیمات ظاهری از روی فهرست مرکزی ساخته می‌شوند.
SiteThemeForm = type(SiteThemeFormBase)(
    "SiteThemeForm",
    (SiteThemeFormBase,),
    {"__module__": __name__, **{token.field_name: theme_override_field(token) for token in ACTIVE_TOKENS}},
)


class AppearanceDirectoryAdmin(admin.ModelAdmin):
    change_form_template = "admin/website/appearance_change_form.html"

    def render_change_form(self, request, context, *args, **kwargs):
        links = (
            ("رنگ‌ها و چیدمان", SiteTheme, True),
            ("متن‌های فارسی و انگلیسی", SiteTexts, True),
            ("برند، لوگو و اطلاعات تماس", SiteSettings, True),
            ("عنوان‌ها و دکمه‌های اول صفحه اصلی", HeroSection, True),
            ("سربرگ و چیدمان منو", MenuItem, False),
            ("معرفی، پرتفولیو و پروژه‌های بیشتر", SiteSection, False),
            ("متن، عکس و گالری هر پروژه", Project, False),
            ("اصول صفحه درباره گارنت", PhilosophyFeature, False),
            ("فایل کاتالوگ شرکت", CompanyCatalog, False),
        )
        context["appearance_links"] = []
        for label, model, singleton in links:
            if model is self.model:
                continue
            target = self.admin_site.get_model_admin(model)
            if not target.has_view_or_change_permission(request):
                continue
            suffix = "changelist"
            arguments = []
            if singleton and model.objects.filter(pk=1).exists():
                suffix, arguments = "change", [1]
            url = reverse(f"{self.admin_site.name}:website_{model._meta.model_name}_{suffix}", args=arguments)
            context["appearance_links"].append((label, url))
        return super().render_change_form(request, context, *args, **kwargs)

    class Media:
        css = {"all": ("css/admin-theme-colors.css",)}
        js = ("js/admin-theme-colors.js",)


@admin.register(SiteTheme)
class SiteThemeAdmin(AppearanceDirectoryAdmin):
    form = SiteThemeForm
    base_fieldsets = (
        ("چیدمان صفحه اصلی و فوتر", {"fields": ("home_project_radius", "compact_footer")}),
        ("🎨 رنگ‌های پایه سایت (پالت اصلی)", {"classes": ("collapse",), "fields": (("background", "surface"), ("primary", "secondary"), ("accent", "accent_hover"), ("text", "muted"), ("white", "dark"), ("border",))}),
        ("🪟 شیشه، شفافیت و عمق", {"classes": ("collapse",), "fields": ("glass", "glass_dark", "overlay", "shadow", ("radius", "glass_blur"))}),
        ("دکمه‌های اصلی و ثانویه", {"classes": ("collapse",), "fields": (("primary_button_background", "primary_button_text"), ("primary_button_hover",), ("glass_button_background", "glass_button_border"))}),
        ("هدر — شفافیت و محوشدگی", {"classes": ("collapse",), "fields": (("header_opacity", "header_blur"),)}),
        ("🖼️ اندازه لوگو", {"classes": ("collapse",), "fields": (("logo_width_desktop", "logo_width_mobile"),)}),
        ("Aa تایپوگرافی و وزن فونت", {"classes": ("collapse",), "fields": (("body_weight", "heading_weight"), ("hero_weight", "section_weight"), ("card_weight", "nav_weight"), ("button_weight", "label_weight"), ("small_weight",)), "description": "وزن‌های قابل استفاده فونت IranSans: 300، 400، 500، 600 و 700."}),
        ("⚙️ سفارشی‌سازی پیشرفته", {"classes": ("collapse",), "fields": ("custom_css",)}),
    )

    def get_fieldsets(self, request, obj=None):
        component_sets = []
        for group in GROUPS:
            fields = [token.field_name for token in group.tokens if token.key not in RETIRED_DECORATIONS]
            if fields:
                component_sets.append((group.title, {
                    "fields": fields, "description": group.description, "classes": ("collapse",),
                }))
        return tuple(component_sets) + self.base_fieldsets

    def has_add_permission(self, request):
        return not SiteTheme.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets=(
        ("برند / Brand",{"fields":("brand_name","legal_name","logo","logo_light","favicon")}),
        ("تماس / Contact",{"fields":("phone","email","address","instagram_url","linkedin_url")}),
        ("چرخش پروژه‌ها / Projects carousel",{"fields":("projects_carousel_enabled","projects_carousel_speed")}),
        ("SEO",{"fields":("meta_title","meta_description")}),
    )
    def has_add_permission(self,request): return not SiteSettings.objects.exists()
    def has_delete_permission(self,request,obj=None): return False

@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    fieldsets=(
        ("فارسی",{"fields":("title","subtitle")}),
        ("English",{"fields":("title_en","subtitle_en")}),
        ("تصویر / ویدیو / Media",{"fields":("background_image","background_video")}),
        ("CTA فارسی",{"fields":(("primary_button_text","primary_button_url"),("secondary_button_text","secondary_button_url"))}),
        ("CTA English",{"fields":(("primary_button_text_en",),("secondary_button_text_en",))}),
    )
    def has_add_permission(self,request): return not HeroSection.objects.exists()
    def has_delete_permission(self,request,obj=None): return False

class ProjectImageInline(admin.TabularInline):
    model=ProjectImage; extra=1; fields=("image","preview","category","caption","caption_en","description","description_en","order"); readonly_fields=("preview",)
    def preview(self,obj): return format_html('<img src="{}" style="height:60px;border-radius:8px;object-fit:cover"/>',obj.image.url) if obj.image else "—"

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display=("title","title_en","status","location","year","is_featured","is_active","purchase_request_enabled","catalog_visible","order"); list_editable=("is_featured","is_active","purchase_request_enabled","catalog_visible","order"); list_filter=("status","is_active","is_featured","purchase_request_enabled","catalog_visible"); search_fields=("title","title_en","code","location","location_en"); prepopulated_fields={"slug":("title",)}; ordering=("order",); inlines=[ProjectImageInline]
    fieldsets=(("فارسی",{"fields":("title","code","slug","status","status_note","location","year","short_description","full_description","feature_list","badge_text","cta_text")}), ("English",{"fields":("title_en","status_note_en","location_en","short_description_en","full_description_en","feature_list_en","badge_text_en","cta_text_en")}), ("معرفی و پیشرفت", {"fields": (("story_title", "story_title_en"), "progress_percent"), "description": "مرحله فعلی از توضیح وضعیت اجرایی، و درصد از همین بخش خوانده می‌شود."}), ("تصویر، کاتالوگ و نمایش",{"fields":("main_image",("catalog_file","catalog_visible"),"purchase_request_enabled","is_featured","is_active","order"),"description":"برای نمایش دکمه کاتالوگ، فایل PDF پروژه و گزینه نمایش باید فعال باشند. عنوان عمومی دکمه از بخش «متن‌های سایت» قابل تغییر است. دکمه درخواست خرید نیز برای هر پروژه جداگانه قابل فعال/غیرفعال‌کردن است."}), ("سیستمی",{"fields":("created_at",)})); readonly_fields=("created_at",)

@admin.register(PhilosophyFeature)
class PhilosophyFeatureAdmin(admin.ModelAdmin):
    list_display=("title","title_en","order","is_active"); list_editable=("order","is_active"); search_fields=("title","title_en","description","description_en"); ordering=("order",)
    fieldsets=(("فارسی",{"fields":("icon_glyph","title","description")}), ("English",{"fields":("title_en","description_en")}), ("نمایش",{"fields":("order","is_active")}))

RETIRED_SITE_SECTIONS = {SiteSection.KEY_PROJECTS_NOTE, SiteSection.KEY_CTA, SiteSection.KEY_WHY_GARNET}


@admin.register(SiteSection)
class SiteSectionAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "title_en", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("key", "title", "title_en", "content", "content_en")

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(key__in=RETIRED_SITE_SECTIONS)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "key":
            kwargs["choices"] = [
                (key, "پروژه‌ها — عنوان و برچسب پرتفولیو" if key == SiteSection.KEY_PROJECTS_HERO else label)
                for key, label in db_field.choices if key not in RETIRED_SITE_SECTIONS
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fields = [("شناسه", {"fields": ("key",)})]
        labels = ("title", "subtitle", "content", "quote_text", "quote_author")
        image = ("image",)
        if obj:
            if obj.key == SiteSection.KEY_PROJECTS_HERO:
                labels, image = ("title", "subtitle"), ()
            elif obj.key in {SiteSection.KEY_PROJECT_DETAIL_CTA, SiteSection.KEY_ABOUT_CTA}:
                labels, image = ("title", "content"), ()
            elif obj.key == SiteSection.KEY_ABOUT_QUOTE:
                labels, image = ("title", "content", "quote_text", "quote_author"), ()
            else:
                labels = ("title", "subtitle", "content")
                if obj.key == SiteSection.KEY_ABOUT_PRINCIPLES:
                    image = ()
        return fields + [
            ("فارسی", {"fields": labels}),
            ("English", {"fields": tuple(field + "_en" for field in labels)}),
            ("نمایش", {"fields": (*image, "is_active")}),
        ]

    def get_readonly_fields(self, request, obj=None):
        return ("key",) if obj else ()


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


class InterfaceCopyFormBase(forms.ModelForm):
    class Meta:
        model = SiteTexts
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        saved = self.instance.interface_copy
        if isinstance(saved, dict):
            for name in INTERFACE_FIELDS:
                value = saved.get(name)
                if isinstance(value, str):
                    self.initial[name] = value

    def clean(self):
        data = super().clean()
        saved = self.instance.interface_copy
        values = dict(saved) if isinstance(saved, dict) else {}
        for name in INTERFACE_FIELDS:
            if name not in data:
                continue
            if data[name]:
                values[name] = data[name]
            else:
                values.pop(name, None)
        self.instance.interface_copy = values
        return data


INTERFACE_FIELDS = {
    f"{key}_{lang}": forms.CharField(
        label=f"{label} ({lang.upper()})", required=False, max_length=250,
        widget=forms.TextInput(attrs={"placeholder": default, "dir": direction}),
    )
    for fields in COPY_GROUPS.values()
    for key, label, fa, en in fields
    for lang, direction, default in (("fa", "rtl", fa), ("en", "ltr", en))
}
InterfaceCopyForm = type(InterfaceCopyFormBase)(
    "InterfaceCopyForm", (InterfaceCopyFormBase,), {"__module__": __name__, **INTERFACE_FIELDS},
)


@admin.register(SiteTexts)
class SiteTextsAdmin(AppearanceDirectoryAdmin):
    form = InterfaceCopyForm
    fieldsets = (
        ("پروژه‌های صفحه اصلی و دکمه خرید فوتر", {"fields": (
            ("home_projects_title", "home_projects_title_en"),
            ("project_view_button", "project_view_button_en"),
            ("footer_purchase_button", "footer_purchase_button_en"),
        )}),
        ("جست‌وجوی پروژه‌ها", {"fields": (
            ("project_search_label", "project_search_label_en"),
            ("project_search_placeholder", "project_search_placeholder_en"),
        )}),
        ("برچسب‌های صفحات پروژه و درباره گارنت", {"fields": (
            ("projects_ongoing_title", "projects_ongoing_title_en"),
            ("projects_completed_title", "projects_completed_title_en"),
            ("project_story_title", "project_story_title_en"),
            ("project_gallery_title", "project_gallery_title_en"),
            ("about_story_link", "about_story_link_en"),
            ("project_buy_label", "project_buy_label_en"),
        )}),
        ("دکمه‌های بخش درباره و همه پروژه‌ها", {"fields": (("home_about_link", "home_about_link_en"), ("all_projects_btn", "all_projects_btn_en"))}),
        ("📘 دکمه کاتالوگ در صفحه داخلی پروژه", {"fields": (("project_catalog_button_text", "project_catalog_button_text_en"),), "description": "عنوان دکمه دانلود کاتالوگ اختصاصی هر پروژه؛ فایل PDF هر پروژه در فرم همان پروژه بارگذاری می‌شود."}),
        ("📞 عنوان دکمه‌های درخواست مشاوره", {"fields": (("consultation_button_text", "consultation_button_text_en"),)}),
        ("📝 پاپ‌آپ فرم درخواست مشاوره", {"fields": (("modal_title","modal_title_en"),("modal_subtitle","modal_subtitle_en"),("submit_text","submit_text_en"),)}),
        ("🏷️ عنوان فیلدهای فرم", {"fields": (("label_name","label_name_en"),("label_gender","label_gender_en"),("label_phone","label_phone_en"),("label_subject","label_subject_en"),("label_message","label_message_en"),)}),
        ("✍️ متن راهنمای داخل فیلدها (Placeholder)", {"fields": (("ph_name","ph_name_en"),("ph_phone","ph_phone_en"),("ph_subject","ph_subject_en"),("ph_message","ph_message_en"),)}),
        ("👤 گزینه‌های فیلد «عنوان»", {"fields": (("opt_male","opt_male_en"),("opt_female","opt_female_en"),("opt_other","opt_other_en"),)}),
    ) + tuple(
        (title, {
            "fields": [(f"{key}_fa", f"{key}_en") for key, *_ in fields],
            "description": "فیلد خالی یعنی نمایش متن پیش‌فرض همان زبان.",
            "classes": ("collapse",),
        })
        for title, fields in COPY_GROUPS.items()
    )

    def has_add_permission(self, request):
        return not SiteTexts.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


def _retired_menu_link_ids(queryset, host):
    return [pk for pk, url in queryset.values_list("pk", "url") if is_retired_blog_link(url, host)]


class MenuSubItemInline(admin.TabularInline):
    model = MenuSubItem
    extra = 0
    fields = ("title", "title_en", "url", "order", "is_active")
    verbose_name = "زیرمنو"
    verbose_name_plural = "زیرمنوها (با کلیک روی آیتم، این گزینه‌ها باز می‌شوند)"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(pk__in=_retired_menu_link_ids(queryset, request.get_host()))


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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        retired = _retired_menu_link_ids(queryset.filter(open_consult=False), request.get_host())
        return queryset.exclude(pk__in=retired)


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
