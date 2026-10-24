from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SiteSettings, HeroSection, HeroStat, Project, ProjectImage,
    PhilosophyFeature, SiteSection, ConsultationRequest, CompanyCatalog, BlogPost, SiteTheme, SiteTexts, MenuItem
)

admin.site.site_header = "پنل مدیریت گارنت | Garnet CMS"
admin.site.site_title = "Garnet Admin"
admin.site.index_title = "مرکز فرمان محتوای سایت گارنت"
admin.site.enable_nav_sidebar = True

from django import forms

class ColorTextInput(forms.TextInput):
    input_type = "color"

class SiteThemeForm(forms.ModelForm):
    class Meta:
        model = SiteTheme
        fields = "__all__"
        widgets = {name: ColorTextInput() for name in (
            "background", "surface", "primary", "secondary", "accent", "accent_hover",
            "text", "muted", "white", "dark", "border"
        )}

    def clean(self):
        data = super().clean()
        for field in ("background", "surface", "primary", "secondary", "accent", "accent_hover", "text", "muted", "white", "dark", "border"):
            value = (data.get(field) or "").strip()
            if not (value.startswith("#") and len(value) in (4, 7)):
                self.add_error(field, "کد HEX معتبر مثل #004E72 وارد کنید.")
        return data



@admin.register(SiteTheme)
class SiteThemeAdmin(admin.ModelAdmin):
    form = SiteThemeForm
    fieldsets = (
        ("🎨 رنگ‌های اصلی سایت", {"fields": (("background", "surface"), ("primary", "secondary"), ("accent", "accent_hover"), ("text", "muted"), ("white", "dark"), ("border",))}),
        ("🪟 شیشه، شفافیت و عمق", {"fields": ("glass", "glass_dark", "overlay", "shadow", ("radius", "glass_blur"), ("modal_background", "modal_border"))}),
        ("▣ هدر و منوی موبایل", {"fields": (("header_background", "header_opacity"), ("header_blur", "header_border"), ("header_text", "header_muted"), ("header_cta_background", "header_cta_text"), ("header_cta_border", "menu_line_color"), ("logo_width_desktop", "logo_width_mobile"))}),
        ("● دکمه‌ها و CTA", {"fields": (("primary_button_background", "primary_button_text"), ("primary_button_hover",), ("glass_button_background", "glass_button_border"))}),
        ("▤ Hero و فوتر", {"fields": (("hero_overlay",), ("footer_background", "footer_text"))}),
        ("Aa تایپوگرافی و وزن فونت", {"fields": (("body_weight", "heading_weight"), ("hero_weight", "section_weight"), ("card_weight", "nav_weight"), ("button_weight", "label_weight"), ("small_weight",)), "description": "وزن‌های قابل استفاده فونت IranSans: 300، 400، 500، 600 و 700."}),
        ("⚙️ سفارشی‌سازی پیشرفته", {"fields": ("custom_css",)}),
    )
    def has_add_permission(self, request):
        return not SiteTheme.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets=(
        ("برند / Brand",{"fields":("brand_name","legal_name","logo","logo_light","favicon",("tagline","tagline_en"))}),
        ("تماس / Contact",{"fields":("phone","email","address","instagram_url","linkedin_url")}),
        ("چرخش پروژه‌ها / Projects carousel",{"fields":("projects_carousel_enabled","projects_carousel_speed","projects_carousel_on_list")}),
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
        ("📝 پاپ‌آپ فرم درخواست مشاوره", {"fields": (("modal_title","modal_title_en"),("modal_subtitle","modal_subtitle_en"),("submit_text","submit_text_en"),)}),
        ("🏷️ عنوان فیلدهای فرم", {"fields": (("label_name","label_name_en"),("label_gender","label_gender_en"),("label_phone","label_phone_en"),("label_subject","label_subject_en"),("label_message","label_message_en"),)}),
        ("✍️ متن راهنمای داخل فیلدها (Placeholder)", {"fields": (("ph_name","ph_name_en"),("ph_phone","ph_phone_en"),("ph_subject","ph_subject_en"),("ph_message","ph_message_en"),)}),
        ("👤 گزینه‌های فیلد «عنوان»", {"fields": (("opt_male","opt_male_en"),("opt_female","opt_female_en"),("opt_other","opt_other_en"),)}),
    )

    def has_add_permission(self, request):
        return not SiteTexts.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """منوی اصلی سایت (هدر دسکتاپ + منوی موبایل): افزودن، حذف، تغییر عنوان/لینک و ترتیب."""
    list_display = ("title", "title_en", "url", "open_consult", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "open_consult")
    search_fields = ("title", "title_en", "url")
    ordering = ("order", "id")
    fieldsets = (
        ("آیتم منو", {"fields": (("title", "title_en"), "url", "open_consult", ("order", "is_active"))}),
    )
