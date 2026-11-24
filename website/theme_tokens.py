"""
website/theme_tokens.py
وظیفه: فهرست مرکزی «رنگ‌های قابل تغییر اجزای سایت».

هر توکن = یک تنظیم ظاهری قابل ویرایش از پنل ادمین (پوسته و طراحی سایت).
- فقط مقدارهایی که مدیر سایت وارد کرده ذخیره می‌شوند؛ فیلد خالی یعنی «ظاهر پیش‌فرض».
- رنگ‌های تغییر داده‌شده و تنظیمات فرم درخواست به متغیرها و قوانین CSS تبدیل می‌شوند.
- مقدارها قبل از ذخیره و دوباره هنگام ساخت CSS اعتبارسنجی
  می‌شوند؛ بنابراین هیچ متن دلخواهی وارد CSS نمی‌شود.
- این فایل عمداً Django را import نمی‌کند تا مستقل تست شود.

افزودن رنگ جدید: فقط یک خط Token به گروه مناسب اضافه کنید (کلید یکتا، برچسب، رنگ پیش‌فرض نمایشی، قانون/قوانین CSS).
در قانون CSS، {v} با مقدار رنگ جایگزین می‌شود.
"""
import re

PALETTE = {
    "charcoal": "#141414",
    "footer-charcoal": "#171717",
    "graphite": "#383838",
    "gray": "#858585",
    "stone": "#E8E7E4",
    "off-white": "#F8F8F6",
    "white": "#FFFFFF",
}
CHARCOAL = PALETTE["charcoal"]
GRAPHITE = PALETTE["graphite"]
STONE = PALETTE["stone"]
OFF_WHITE = PALETTE["off-white"]
WHITE = PALETTE["white"]


HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
RGB_RE = re.compile(
    r"^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*(0|1|0?\.\d{1,3}|1\.0{1,3})\s*)?\)$",
    re.IGNORECASE,
)


def normalize_color(value):
    """مقدار رنگ معتبر (به‌صورت تمیز) یا None برمی‌گرداند. ورودی خالی => None."""
    if value is None:
        return None
    value = str(value).strip()
    if not value or len(value) > 40:
        return None
    if value.lower() == "transparent":
        return "transparent"
    if HEX_RE.match(value):
        return value.lower()
    match = RGB_RE.match(value)
    if match:
        r, g, b = (int(match.group(i)) for i in (1, 2, 3))
        if max(r, g, b) <= 255:
            return re.sub(r"\s+", "", value.lower())
    return None


class Token:
    normalize = staticmethod(normalize_color)
    __slots__ = ("key", "label", "default", "rules")

    def __init__(self, key, label, default, rules):
        self.key = key
        self.label = label
        self.default = default
        self.rules = tuple(rules) if isinstance(rules, (list, tuple)) else (rules,)

    @property
    def field_name(self):
        return "c_" + self.key


class PixelToken(Token):
    __slots__ = ("minimum", "maximum")

    def __init__(self, key, label, default, minimum, maximum, property_name):
        super().__init__(key, label, str(default), "#consultModal{" + property_name + ":{v}px}")
        self.minimum = minimum
        self.maximum = maximum

    def normalize(self, value):
        value = str(value).strip()
        if re.fullmatch(r"[0-9]{1,4}", value) and self.minimum <= int(value) <= self.maximum:
            return str(int(value))
        return None


def modal_color(key, label, default):
    property_name = "--request-" + key.replace("_", "-")
    return Token("request_" + key, label, default, "#consultModal{" + property_name + ":{v}}")


class Group:
    __slots__ = ("key", "title", "description", "tokens")

    def __init__(self, key, title, description, tokens):
        self.key = key
        self.title = title
        self.description = description
        self.tokens = tokens


# ---------------------------------------------------------------------------
# فهرست رنگ‌ها. هر Token: (کلید، برچسب فارسی، رنگ پیش‌فرض نمایشی، قوانین CSS)
# ---------------------------------------------------------------------------
GROUPS = [
    Group("backgrounds", "🖼️ پس‌زمینه صفحه‌ها و بخش‌ها",
          "رنگ زمینه‌ی کل سایت و هر بخش یا صفحه به‌صورت جداگانه. فیلد خالی = رنگ پیش‌فرض.", [
        Token("page_bg", "پس‌زمینه کل سایت", OFF_WHITE, "body.site-shell{background:{v}!important}"),
        Token("sec_home_projects_bg", "بخش «گارنت، در یک نگاه» (کل پروژه‌ها) در صفحه اصلی", OFF_WHITE,
              ".section.home-projects{background:{v}!important}"),
        Token("sec_about_bg", "رنگ مشترک انتهای ویدیو و پس‌زمینه «درباره گارنت»", "#101111",
              "body.site-home{--home-seam:{v}}"),
        Token("page_projects_bg", "صفحه «پروژه‌ها» (لیست پروژه‌ها)", OFF_WHITE,
              ".section.projects-page{background:{v}!important}"),
        Token("page_project_detail_bg", "صفحه داخلی هر پروژه (بخش متن و اطلاعات)", OFF_WHITE,
              ".section.pd-body{background:{v}!important}"),
    ]),
    Group("texts", "🔤 رنگ تیترها و متن‌های عمومی", "تیتر بخش‌ها، لینک‌ها و متن‌های صفحه‌ها.", [
        Token("text_body", "متن عمومی سایت", CHARCOAL, "body.site-shell{color:{v}!important}"),
        Token("text_heading", "تیتر بخش‌ها و صفحه‌ها",
              CHARCOAL, ".compact-heading h1,.compact-heading h2,.compact-heading h3{color:{v}!important}"),
        Token("text_section_link", "پیوندهای کنار تیتر", CHARCOAL,
              ".compact-heading .section-link{color:{v}!important}"),
        Token("text_empty_state", "پیام‌های خالی (مثل «پروژه‌ای ثبت نشده»)", GRAPHITE,
              ".empty-state,.projects-block .empty-state{color:{v}!important}"),
    ]),
    Group("header", "▣ هدر (نوار بالای سایت) و منوی دسکتاپ", "نوار شیشه‌ای بالای سایت، لینک‌های منو و دکمه مشاوره.", [
        Token("header_bg", "پس‌زمینه نوار هدر", WHITE,
              ".g-header{--header-strip-tint:{v}}"),
        Token("header_border", "خط دور نوار هدر", "rgba(255,255,255,.34)", ".g-header .g-bar{border-color:{v}!important}"),
        Token("header_link", "رنگ لینک‌های منو", CHARCOAL,
              ".g-header{--header-strip-ink:{v}}"),
        Token("header_link_hover", "رنگ لینک منو هنگام نگه‌داشتن ماوس / صفحه فعال", GRAPHITE,
              ".g-header{--header-strip-hover:{v}}"),
        Token("header_underline", "خط زیر لینک فعال منو", CHARCOAL,
              ".g-header{--header-strip-rule:{v}}"),
        Token("header_brand_text", "نام برند (وقتی لوگو آپلود نشده)", CHARCOAL, ".g-header .g-brand{--header-brand-tint:{v}}"),
        Token("header_cta_bg", "دکمه «درخواست مشاوره» — پس‌زمینه", CHARCOAL,
              ".g-header .g-cta{background:{v}!important;background-image:none!important}"),
        Token("header_cta_hover", "دکمه «درخواست مشاوره» — پس‌زمینه هنگام Hover", GRAPHITE,
              ".g-header .g-cta:hover{background:{v}!important;background-image:none!important;filter:none!important}"),
        Token("header_cta_text", "دکمه «درخواست مشاوره» — رنگ متن", WHITE, ".g-header .g-cta,.g-header .g-cta span{color:{v}!important}"),
        Token("header_cta_border", "دکمه «درخواست مشاوره» — رنگ لبه", "rgba(255,255,255,.2)", ".g-header{--header-buy-border:{v}}"),
        Token("header_hero_link", "رنگ منو و جست‌وجو پیش از اسکرول روی زمینه تیره", WHITE, ".g-header{--header-hero-ink:{v}}"),
        Token("header_hero_hover", "رنگ گزینه فعال یا هاور روی زمینه تیره", WHITE, ".g-header{--header-hero-hover:{v}}"),
        Token("header_buy_surface", "دکمه درخواست خرید — زمینه", "transparent", ".g-header{--header-buy-bg:{v}}"),
        Token("header_buy_hover", "دکمه درخواست خرید — زمینه هنگام هاور", "rgba(255,255,255,.1)", ".g-header{--header-buy-hover:{v}}"),
        Token("header_buy_ink", "دکمه درخواست خرید — نوشته", OFF_WHITE, ".g-header{--header-buy-ink:{v}}"),
        Token("header_dropdown_bg", "زیرمنوی پروژه‌ها (دسکتاپ) — پس‌زمینه", WHITE, ".g-header .g-sub{background:{v}!important}"),
        Token("header_dropdown_border", "زیرمنوی پروژه‌ها (دسکتاپ) — لبه", STONE, ".g-header .g-sub{border-color:{v}!important}"),
        Token("header_dropdown_text", "زیرمنوی پروژه‌ها (دسکتاپ) — متن", CHARCOAL, ".g-header .g-sub a{color:{v}!important}"),
        Token("header_dropdown_hover", "زیرمنوی پروژه‌ها (دسکتاپ) — پس‌زمینه گزینه هنگام Hover", STONE,
              ".g-header .g-sub a:hover,.g-header .g-sub a:focus-visible{background:{v}!important}"),
    ]),
    Group("mobile_menu", "☰ منوی موبایل (دکمه سه‌خط و پنل باز شونده)", "ظاهر منو در موبایل و تبلت.", [
        Token("toggle_lines", "رنگ سه‌خط منو (همبرگری)", CHARCOAL, ".g-header{--header-strip-toggle:{v}}"),
        Token("toggle_bg", "پس‌زمینه دکمه سه‌خط", WHITE, ".g-header .g-toggle{--header-toggle-tint:{v}}"),
        Token("toggle_border", "لبه دکمه سه‌خط", "rgba(255,255,255,.18)", ".g-header .g-toggle{border-color:{v}!important}"),
        Token("panel_bg", "پس‌زمینه پنل منو", WHITE, ".g-header .g-mobile-panel{background:{v}!important}"),
        Token("panel_border", "لبه پنل منو", STONE, ".g-header .g-mobile-panel{border-color:{v}!important}"),
        Token("panel_item_bg", "پس‌زمینه گزینه‌های پنل", "rgba(255,255,255,.06)",
              ".g-header .g-mobile-panel a,.g-header .g-mobile-panel .g-panel-btn{background:{v}!important}"),
        Token("panel_item_hover", "گزینه‌های پنل هنگام لمس / فعال", STONE,
              ".g-header .g-mobile-panel a:hover,.g-header .g-mobile-panel a.is-active,.g-header .g-mobile-panel .g-panel-btn:hover{background:{v}!important}"),
        Token("panel_item_text", "متن گزینه‌های پنل", CHARCOAL,
              ".g-header .g-mobile-panel a,.g-header .g-mobile-panel .g-panel-btn{color:{v}!important}"),
        Token("panel_sub_bg", "زیرگزینه‌های پروژه‌ها در پنل — پس‌زمینه", "rgba(255,255,255,.1)", ".g-header .g-mobile-panel .g-panel-sub a{background:{v}!important}"),
    ]),
    Group("hero", "🎬 بخش اصلی (Hero) صفحه اصلی", "تیتر، توضیح و دکمه‌های روی تصویر/ویدیوی اول صفحه.", [
        Token("hero_shade", "پوشش بالای تصویر یا ویدیوی اول", "rgba(0,0,0,.28)", ".g-home-hero{--home-hero-shade:{v}}"),
        Token("hero_title", "تیتر اصلی", "#FFFFFF", ".hero h1{color:{v}!important}"),
        Token("hero_text", "متن زیر تیتر", "rgba(255,255,255,.78)", ".hero .hero-copy>p{color:{v}!important}"),
        Token("hero_btn_text", "متن دکمه‌های شیشه‌ای Hero", WHITE, ".hero .hero-action-link{color:{v}!important}"),
        Token("home_glass_bg", "پس‌زمینه دکمه‌های روی ویدیو", "rgba(255,255,255,.12)", ".g-home-hero{--home-glass-bg:{v}}"),
        Token("home_glass_border", "لبه دکمه‌های روی ویدیو", "rgba(255,255,255,.52)", ".g-home-hero{--home-glass-border:{v}}"),
        Token("hero_btn_hover", "دکمه‌های Hero هنگام Hover", "rgba(255,255,255,.24)", ".hero .hero-action-link:hover{background:{v}!important}"),
    ]),
    Group("preview_cards", "🏗️ کارت‌های پیش‌نمایش پروژه در صفحه اصلی",
          "وضعیت، عنوان، موقعیت و دکمه مشاهدهٔ کارت‌های صفحه اصلی.", [
        Token("card_bg", "زمینه کارت (پشت تصویر / وقتی تصویر ندارد) — هماهنگ با بخش درباره گارنت", OFF_WHITE,
              ".mini-project.project-preview{background:{v}!important;background-image:none!important}"),
        Token("card_shadow", "سایه کارت‌های پیش‌نمایش (برای حذف سایه rgba(0,0,0,0) وارد کنید)", "rgba(0,0,0,0)",
              ".mini-project.project-preview,.mini-project.project-preview:hover{box-shadow:0 12px 28px {v}!important}"),
        Token("card_title", "عنوان روی کارت", "#FFFFFF", ".mini-project.project-preview .pc-bottom h3{color:{v}!important}"),
        Token("card_location", "موقعیت / تاریخ روی کارت", "#FFFFFF", ".mini-project.project-preview .pc-loc{color:{v}!important}"),
        Token("card_status_ongoing_bg", "نشان «در حال اجرا» — پس‌زمینه", "rgba(34,70,58,.5)", ".mini-project.project-preview .pc-status.pc-ongoing{background:{v}!important}"),
        Token("card_status_ongoing_dot", "نشان «در حال اجرا» — نقطه", "#2CF08A", ".mini-project.project-preview .pc-status.pc-ongoing i{background:{v}!important;box-shadow:0 0 9px {v}!important}"),
        Token("card_status_completed_bg", "نشان «به اتمام رسیده» — پس‌زمینه", "rgba(30,52,82,.5)", ".mini-project.project-preview .pc-status.pc-completed{background:{v}!important}"),
        Token("card_status_completed_dot", "نشان «به اتمام رسیده» — نقطه", "#7CC4FF", ".mini-project.project-preview .pc-status.pc-completed i{background:{v}!important;box-shadow:0 0 9px {v}!important}"),
        Token("card_status_text", "متن نشان وضعیت", "#FFFFFF", ".mini-project.project-preview .pc-status{color:{v}!important}"),
        Token("card_btn_bg", "دکمه «مشاهده» — پس‌زمینه", WHITE, ".mini-project.project-preview .pc-view{background:{v}!important}"),
        Token("card_btn_text", "دکمه «مشاهده» — متن و فلش", CHARCOAL,
              ".mini-project.project-preview .pc-view,.mini-project.project-preview .pc-view span,.mini-project.project-preview .pc-view em,.mini-project.project-preview .pc-view svg{color:{v}!important;stroke:{v}!important}"),
        Token("card_btn_circle", "دایره‌ی فلش در دکمه «مشاهده»", "#FFFFFF", ".mini-project.project-preview .pc-view em{background:{v}!important}"),
    ]),
    Group("rail_buttons", "دکمه مشاهده همه پروژه‌ها", "رنگ پیوند فهرست پروژه‌ها در صفحه اصلی.", [
        Token("all_btn_bg", "دکمه «مشاهده همه پروژه‌ها» — پس‌زمینه", "transparent",
              ".all-projects-btn{background:{v}!important;background-image:none!important}"),
        Token("all_btn_icon", "دکمه «مشاهده همه پروژه‌ها» — متن و آیکون", CHARCOAL, ".all-projects-btn{color:{v}!important}"),
        Token("rail_nav_bg", "فلش‌های چپ/راست ردیف — پس‌زمینه", WHITE, ".rail-nav{background:{v}!important}"),
        Token("rail_nav_icon", "فلش‌های چپ/راست ردیف — آیکون", CHARCOAL, ".rail-nav{color:{v}!important}"),
    ]),
    Group("about", "🏛️ بخش «درباره گارنت»", "تیتر، متن و دکمه بخش درباره گارنت در صفحه اصلی.", [
        Token("about_title", "عنوان", "#F7F7F5", ".g-home-manifesto h2{color:{v}!important}"),
        Token("about_text", "متن", "#B7B9B7", ".g-home-manifesto-summary{color:{v}!important}"),
        Token("about_kicker", "متن کوتاه بالای عنوان", "#B5B2AB", ".g-home-manifesto-kicker{color:{v}!important}"),
        Token("about_btn_light_bg", "دکمه درباره — پس‌زمینه", "transparent", ".g-home-manifesto-link{background:{v}}"),
        Token("about_btn_light_text", "دکمه درباره — متن", WHITE, ".g-home-manifesto-link{color:{v}!important}"),
        Token("about_card_border", "دکمه درباره — رنگ لبه", "#6A6E6B", ".g-home-manifesto-link{border-color:{v}!important}"),
        Token("about_card_bg", "پس‌زمینه کادر نسخه قبلی", "rgba(255,255,255,.88)", ()),
        Token("about_btn_main_bg", "پس‌زمینه دکمه پروژه‌های نسخه قبلی", CHARCOAL, ()),
        Token("about_btn_main_text", "متن دکمه پروژه‌های نسخه قبلی", WHITE, ()),
    ]),
    Group("projects_page", "صفحهٔ پروژه‌ها — طرح قبلی", "برای طرح فعلی از گروه «صفحات پروژه‌ها و درباره گارنت» استفاده کنید.", [
        Token("tabs_bg", "کپسول‌های «در حال اجرا / تمام شده» — پس‌زمینه", "#FFFFFF", ".projects-tabs a{background:{v}!important}"),
        Token("tabs_text", "کپسول‌های «در حال اجرا / تمام شده» — متن", "#0B2A3A", ".projects-tabs a{color:{v}!important}"),
        Token("tabs_count_bg", "شمارنده کپسول‌ها", "#0B2A3A", ".projects-tabs b{background:{v}!important}"),
        Token("block_heading", "تیتر هر گروه (پروژه‌های در حال اجرا / اتمام شده)", "#0B2A3A", ".projects-block-head h2{color:{v}!important}"),
        Token("row_bg", "ردیف پروژه — پس‌زمینه", "#FFFFFF", ".proj-row{background:{v}!important}"),
        Token("row_shadow", "سایه ردیف پروژه (برای حذف سایه rgba(0,0,0,0) وارد کنید)", "rgba(0,0,0,0)", ".proj-row,.proj-row:hover{box-shadow:0 18px 44px {v}!important}"),
        Token("row_border", "ردیف پروژه — لبه", "rgba(9,38,52,.1)", ".proj-row{border-color:{v}!important}"),
        Token("row_title", "ردیف پروژه — عنوان", CHARCOAL, ".proj-row .proj-row-title{color:{v}!important}"),
        Token("row_text", "ردیف پروژه — توضیح", GRAPHITE, ".proj-row .proj-row-desc{color:{v}!important}"),
        Token("row_meta", "ردیف پروژه — موقعیت و اطلاعات", GRAPHITE, ".proj-row .proj-row-meta,.proj-row .proj-row-meta span{color:{v}!important}"),
        Token("row_btn_bg", "ردیف پروژه — دکمه مشاهده", CHARCOAL, ".proj-row .proj-row-btn{background:{v}!important}"),
        Token("row_btn_text", "ردیف پروژه — متن دکمه مشاهده", "#FFFFFF", ".proj-row .proj-row-btn,.proj-row .proj-row-btn span,.proj-row .proj-row-btn svg{color:{v}!important}"),
        Token("row_status_ongoing", "ردیف پروژه — نشان «در حال اجرا»", CHARCOAL,
              ".proj-row .proj-row-status.ps-ongoing{color:{v}!important;border-color:{v}!important}"),
        Token("row_status_ongoing_dot", "ردیف پروژه — نقطه‌ی «در حال اجرا»", "#2CF08A",
              ".proj-row .proj-row-status.ps-ongoing i{background:{v}!important;box-shadow:0 0 9px {v}!important}"),
        Token("row_status_completed", "ردیف پروژه — نشان «به اتمام رسیده»", CHARCOAL,
              ".proj-row .proj-row-status.ps-completed{color:{v}!important;border-color:{v}!important}"),
        Token("row_status_completed_dot", "ردیف پروژه — نقطه‌ی «به اتمام رسیده»", "#7CC4FF",
              ".proj-row .proj-row-status.ps-completed i{background:{v}!important;box-shadow:0 0 9px {v}!important}"),
        Token("row_badge_bg", "ردیف پروژه — نشان ویژه روی تصویر", CHARCOAL, ".proj-row .proj-row-badge{background:{v}!important}"),
    ]),
    Group("project_detail", "جزئیات پروژه — طرح قبلی", "برای طرح فعلی از گروه «صفحات پروژه‌ها و درباره گارنت» استفاده کنید.", [
        Token("pd_story_title", "عنوان متن پروژه", "#1A1C1C", ".pd-story h2{color:{v}!important}"),
        Token("pd_text", "متن معرفی پروژه", "#425661", ".pd-text p{color:{v}!important}"),
        Token("pd_aside_bg", "کادر «اطلاعات پروژه» — پس‌زمینه", "#FFFFFF", ".pd-aside{background:{v}!important}"),
        Token("pd_aside_border", "کادر «اطلاعات پروژه» — لبه", "rgba(7,29,43,.08)", ".pd-aside{border-color:{v}!important}"),
        Token("pd_aside_title", "کادر «اطلاعات پروژه» — عنوان", "#0B2A3A", ".pd-aside h3{color:{v}!important}"),
        Token("pd_aside_text", "کادر «اطلاعات پروژه» — متن", "#33474F", ".pd-features li{color:{v}!important}"),
        Token("pd_btn_main_bg", "دکمه بالای صفحه پروژه (مشاوره) — پس‌زمینه", CHARCOAL, ".pd-btn.pd-btn-primary{background:{v}!important;background-image:none!important}"),
        Token("pd_btn_glass_bg", "دکمه شیشه‌ای (گالری) — پس‌زمینه", WHITE, ".pd-btn.pd-btn-glass{background:{v}!important}"),
        Token("pd_btn_text", "متن دکمه‌های بالای صفحه پروژه", "#FFFFFF", ".pd-btn,.pd-btn .pd-btn-label{color:{v}!important}"),
        Token("pd_btn_shadow", "رنگ سایه دکمه درخواست خرید / مشاوره", "rgba(150,80,45,.38)", ".pd-btn.pd-btn-primary,.pd-cta{box-shadow:0 12px 32px {v}!important}"),
        Token("pd_btn_pulse", "رنگ هاله ضربانی دکمه درخواست خرید / مشاوره", "rgba(204,108,66,.42)", ".pd-btn.pd-btn-primary::after,.pd-cta::after{border-color:{v}!important}"),
        Token("pd_chip_bg", "کپسول‌های کد / وضعیت / سال", "rgba(20,26,30,.28)", ".pd-chips li{background:{v}!important}"),
    ]),
    Group("project_presentation", "رنگ صفحات پروژه‌ها",
          "پالت مشترک فهرست و جزئیات پروژه. زمینه و متن «پروژه‌های بیشتر» مستقل‌اند.", [
        Token("project_" + key, label, color,
              ".editorial-portfolio,.editorial-detail{--project-theme-" + key.replace("_", "-") + ":{v}}")
        for key, label, color in (
            ("dark", "زمینهٔ تیرهٔ بالای صفحات", CHARCOAL),
            ("dark_surface", "سطح تیرهٔ پیشرفت پروژه و نمایشگر گالری", "#222222"),
            ("dark_ink", "متن اصلی روی زمینهٔ تیره", OFF_WHITE),
            ("dark_muted", "متن فرعی روی زمینهٔ تیره", "#CCC9C1"),
            ("dark_line", "خط و حاشیه روی زمینهٔ تیره", "#4B4A47"),
            ("light", "زمینهٔ شیری فهرست، معرفی و گالری", "#F4F1EA"),
            ("light_surface", "سطح روشن جست‌وجو و دسته‌بندی پروژه‌ها", "#FBF9F4"),
            ("light_ink", "متن اصلی، دکمه‌ها و آیکون‌ها روی زمینهٔ روشن", CHARCOAL),
            ("light_muted", "متن فرعی روی زمینهٔ روشن", "#55534F"),
            ("light_line", "خط و حاشیه روی زمینهٔ روشن", "#D1CCC2"),
            ("related_bg", "پروژه‌های بیشتر — رنگ زمینه", CHARCOAL),
            ("related_ink", "پروژه‌های بیشتر — رنگ متن و دکمه", OFF_WHITE),
        )
    ]),
    Group("gallery", "نمایشگر عکس پروژه", "رنگ پنجره، نوشته و دکمه‌های جابه‌جایی عکس.", [
        Token("gallery_surface", "زمینه قاب و نوار پایین", CHARCOAL, ".project-gallery-viewer{--viewer-surface:{v}}"),
        Token("gallery_ink", "رنگ عنوان عکس", OFF_WHITE, ".project-gallery-viewer{--viewer-ink:{v}}"),
        Token("gallery_muted", "رنگ توضیح و شمارنده عکس", "#CCC9C1", ".project-gallery-viewer{--viewer-muted:{v}}"),
        Token("gallery_veil", "رنگ پرده پشت نمایشگر", "rgba(20,20,20,.86)", ".project-gallery-viewer::backdrop{background:{v}}"),
        Token("gallery_arrow_bg", "پس‌زمینه فلش‌های چپ و راست", "rgba(20,20,20,.55)", ".project-gallery-viewer{--viewer-arrow-bg:{v}}"),
        Token("gallery_arrow_ink", "رنگ فلش‌ها", OFF_WHITE, ".project-gallery-viewer{--viewer-arrow-ink:{v}}"),
        Token("gallery_close_bg", "پس‌زمینه دکمه بستن", "rgba(20,20,20,.8)", ".project-gallery-viewer{--viewer-close-bg:{v}}"),
        Token("gallery_close_ink", "رنگ ضربدر بستن", OFF_WHITE, ".project-gallery-viewer{--viewer-close-ink:{v}}"),
    ]),
    Group("editorial_pages", "رنگ صفحه درباره گارنت",
          "رنگ‌های محتوای صفحه درباره گارنت. هدر و فوتر از کنترل‌های مشترک خود استفاده می‌کنند.", [
        Token("editorial_canvas", "رنگ زمینه و انتهای تصویر آغاز صفحه", "#101411", ".editorial-about{--ed-theme-canvas:{v}}"),
        Token("editorial_volume", "رنگ عمق بخش‌ها و زمینه کارت‌ها", "#263028", ".editorial-about{--ed-theme-volume:{v}}"),
        Token("editorial_ink", "رنگ تیترها و دکمه‌های متنی", "#F4F3EF", ".editorial-about{--ed-theme-ink:{v}}"),
        Token("editorial_muted", "رنگ توضیحات", "#C1C8BF", ".editorial-about{--ed-theme-muted:{v}}"),
        Token("editorial_accent", "رنگ تأکیدی و نوار پیشرفت", "#C6BCA9", ".editorial-about{--ed-theme-accent:{v}}"),
    ]),
    Group("about_sections", "رنگ بخش‌های صفحه درباره گارنت",
          "زمینه، تیتر و توضیح هر بخش به‌صورت جداگانه. فیلد خالی از پالت صفحه درباره استفاده می‌کند.", [
        Token(f"about_{key}_{part}", f"{label} — {part_label}", color,
              f".editorial-about [data-about-section={key}]{{{property_name}:{{v}}}}")
        for key, label in (
            ("story", "داستان برند"), ("philosophy", "فلسفه و تصویر"),
            ("principles", "اصول"), ("quote", "نقل‌قول"), ("cta", "بخش پایانی"),
        )
        for part, part_label, color, property_name in (
            ("bg", "زمینه", "#101411", "--about-band-bg"),
            ("ink", "تیتر و دکمه", "#F4F3EF", "--ed-ink"),
            ("muted", "توضیحات", "#C1C8BF", "--ed-muted"),
        )
    ]),
    Group("project_controls", "جست‌وجو، کارت‌ها و پیشرفت پروژه",
          "رنگ عناصر داخل فهرست و صفحه جزئیات پروژه.", [
        Token("project_search_bg", "زمینه فیلد جست‌وجو", "#F4F1EA", ".editorial-portfolio .ed-project-search{--search-surface:{v}}"),
        Token("project_search_ink", "متن فیلد جست‌وجو", CHARCOAL, ".editorial-portfolio .ed-project-search{--search-ink:{v}}"),
        Token("project_search_placeholder", "راهنمای فیلد جست‌وجو", GRAPHITE, ".editorial-portfolio .ed-project-search{--search-placeholder:{v}}"),
        Token("project_search_border", "لبه فیلد جست‌وجو", STONE, ".editorial-portfolio .ed-project-search{--search-border:{v}}"),
        Token("project_card_badge_bg", "زمینه نشان وضعیت و کد پروژه", CHARCOAL, ".editorial-portfolio,.editorial-detail{--project-badge-bg:{v}}"),
        Token("project_card_badge_ink", "متن نشان وضعیت و کد پروژه", OFF_WHITE, ".editorial-portfolio,.editorial-detail{--project-badge-ink:{v}}"),
        Token("project_progress_surface", "زمینه کادر پیشرفت اجرایی", CHARCOAL, ".editorial-detail .ed-progress{--project-progress-surface:{v}}"),
        Token("project_progress_fill", "رنگ خط پیشرفت و عدد درصد", OFF_WHITE, ".editorial-detail .ed-progress{--ed-accent:{v}}"),
    ]),
    Group("footer", "⬛ فوتر (پایین سایت)", "رنگ زمینه، تیترها، لینک‌ها، آیکون‌ها و فرم خبرنامه.", [
        Token("footer_bg", "پس‌زمینه فوتر", PALETTE["footer-charcoal"], ".site-footer{--footer-surface-override:{v}}"),
        Token("footer_text", "متن‌های فوتر", "#FFFFFF", ".site-footer{--footer-ink-override:{v}}"),
        Token("footer_heading", "تیترهای ستون‌های فوتر", "#FFFFFF", ".site-footer .footer-col h2{color:{v}!important}"),
        Token("footer_link", "لینک‌ها و متن ستون‌ها", "rgba(255,255,255,.66)",
              ".site-footer .footer-grid-reference .footer-col-body>a,.site-footer .footer-grid-reference .footer-col-body>p{color:{v}!important}"),
        Token("footer_link_hover", "لینک‌ها هنگام Hover", "#FFFFFF",
              ".site-footer .footer-grid-reference .footer-col-body>a:hover{color:{v}!important}"),
        Token("footer_contact_icon", "آیکون تلفن و ایمیل", WHITE, ".site-footer .footer-contact-icon{color:{v}!important}"),
        Token("footer_buy_bg", "دکمه درخواست خرید فوتر — پس‌زمینه", WHITE, ".site-footer .footer-buy{--footer-buy-bg:{v}}"),
        Token("footer_buy_text", "دکمه درخواست خرید فوتر — رنگ متن", CHARCOAL, ".site-footer .footer-buy{--footer-buy-text:{v}}"),
        Token("footer_buy_hover", "دکمه درخواست خرید فوتر — پس‌زمینه هنگام Hover", STONE, ".site-footer .footer-buy{--footer-buy-hover:{v}}"),
        Token("footer_social", "آیکون‌های اینستاگرام و لینکدین", "#FFFFFF", ".site-footer .footer-social-links a{color:{v}!important}"),
        Token("footer_news_bg", "فرم خبرنامه — پس‌زمینه", "#FFFFFF", ".site-footer .newsletter-form{--newsletter-surface-tint:{v}}"),
        Token("footer_news_text", "فرم خبرنامه — رنگ متن ایمیل", CHARCOAL, ".site-footer .newsletter-form{--newsletter-text-tint:{v}}"),
        Token("footer_news_btn", "فرم خبرنامه — دکمه ثبت", CHARCOAL, ".site-footer .newsletter-form{--newsletter-action-tint:{v}}"),
        Token("footer_news_placeholder", "فرم خبرنامه — رنگ راهنمای ایمیل", GRAPHITE, ".site-footer .newsletter-form{--newsletter-placeholder:{v}}"),
        Token("footer_news_btn_text", "فرم خبرنامه — نوشته و فلش دکمه", WHITE, ".site-footer .newsletter-form{--newsletter-action-ink:{v}}"),
        Token("footer_news_btn_hover", "فرم خبرنامه — رنگ هاور دکمه", GRAPHITE, ".site-footer .newsletter-form{--newsletter-action-hover:{v}}"),
        Token("footer_divider", "خط بین ستون‌ها و بخش‌های فوتر", "rgba(255,255,255,.15)", ".site-footer{--footer-divider-override:{v}}"),
        Token("footer_bottom_text", "نوار پایین فوتر (کپی‌رایت و زبان)", "rgba(255,255,255,.66)", ".site-footer .footer-bottom,.site-footer .footer-bottom small,.site-footer .footer-bottom a{color:{v}!important}"),
        Token("footer_bottom_line", "خط بالای نوار پایین فوتر", "rgba(255,255,255,.09)", ".site-footer .footer-bottom{border-top-color:{v}!important}"),
    ]),
    Group("modal", "فرم ثبت درخواست",
          "رنگ، شفافیت، محوشدگی و اندازه‌های فرم مشترک. برای رنگ شیشه rgba وارد کنید؛ "
          "برای دکمه بدون زمینه transparent بنویسید. فیلد خالی به مقدار پیش‌فرض برمی‌گردد.", [
        modal_color("veil", "پرده پشت فرم — رنگ و شفافیت", "rgba(20,20,20,.28)"),
        modal_color("glass_tint", "شیشهٔ فرم — رنگ و شفافیت", "rgba(248,248,246,.94)"),
        modal_color("solid_surface", "پس‌زمینه جایگزین در مرورگرهای بدون Blur", OFF_WHITE),
        modal_color("frame", "لبه کادر فرم", "rgba(255,255,255,.68)"),
        modal_color("shadow", "رنگ و شدت سایهٔ فرم", "rgba(20,20,20,.22)"),
        modal_color("divider", "خط جداکنندهٔ فرم", "transparent"),
        modal_color("title", "تیتر فرم", CHARCOAL),
        modal_color("subtitle", "توضیح زیر تیتر", "#494947"),
        modal_color("label", "عنوان فیلدها و گزینه‌ها", CHARCOAL),
        modal_color("required", "نشان فیلد الزامی", "#494947"),
        modal_color("input_bg", "فیلدهای ورودی و گزینه‌ها — پس‌زمینه", "rgba(255,255,255,.44)"),
        modal_color("field_line", "فیلدهای ورودی — رنگ خط زیر فیلد", "rgba(20,20,20,.50)"),
        modal_color("input_text", "فیلدهای ورودی — متن", CHARCOAL),
        modal_color("placeholder", "راهنمای داخل فیلدها — رنگ متن", "#575754"),
        modal_color("option_selected", "گزینهٔ انتخاب‌شده — پس‌زمینه", "transparent"),
        modal_color("focus", "فوکوس کیبورد و گزینهٔ انتخاب‌شده — رنگ تأکید", CHARCOAL),
        modal_color("error", "پیام خطا و لبهٔ فیلد نامعتبر", "#86271f"),
        modal_color("action_bg", "دکمه ثبت درخواست — پس‌زمینه", "transparent"),
        modal_color("action_line", "دکمه ثبت درخواست — رنگ خط زیر دکمه", "rgba(20,20,20,.50)"),
        modal_color("action_text", "دکمه ثبت درخواست — متن و آیکون", CHARCOAL),
        modal_color("action_hover", "دکمه ثبت درخواست — پس‌زمینه هنگام هاور", "rgba(20,20,20,.06)"),
        modal_color("close_bg", "دکمه بستن — پس‌زمینه", "transparent"),
        modal_color("close_line", "دکمه بستن — رنگ خط زیر دکمه", "transparent"),
        modal_color("close_text", "دکمه بستن — رنگ آیکون", CHARCOAL),
        modal_color("close_hover", "دکمه بستن — پس‌زمینه هنگام هاور", "rgba(20,20,20,.07)"),
        PixelToken("modal_blur", "محوشدگی شیشهٔ فرم (px)", 16, 0, 32, "--request-blur"),
        PixelToken("modal_width", "حداکثر عرض فرم (px)", 672, 420, 800, "--request-width"),
        PixelToken("modal_padding", "حداکثر فاصلهٔ داخلی فرم (px)", 32, 16, 48, "--request-padding"),
        PixelToken("modal_gap", "فاصلهٔ ردیف‌های فرم (px)", 14, 8, 24, "--request-gap"),
        PixelToken("modal_panel_radius", "گردی گوشه‌های کادر فرم (px)", 4, 0, 24, "--request-panel-radius"),
        PixelToken("modal_control_radius", "گردی گوشه‌های دکمه‌ها و فیلدها (px)", 0, 0, 16, "--request-control-radius"),
        PixelToken("modal_control_size", "حداقل ارتفاع فیلدها و دکمه‌ها (px)", 44, 44, 64, "--request-control-size"),
    ]),
    Group("floating", "🔘 دکمه‌های شناور و پیام‌ها", "دکمهٔ تماس و پیام‌های موفقیت و خطا.", [
        Token("float_call_bg", "دکمه گرد تماس — پس‌زمینه", CHARCOAL, ".floating-call{background:{v}!important;background-image:none!important}"),
        Token("float_call_icon", "دکمه گرد تماس — آیکون", "#FFFFFF", ".floating-call{color:{v}!important}"),
        Token("back_btn_bg", "دکمه «بازگشت» — پس‌زمینه", WHITE, ".mobile-back{background:{v}!important}"),
        Token("back_btn_text", "دکمه «بازگشت» — متن", CHARCOAL, ".mobile-back,.mobile-back b{color:{v}!important}"),
        Token("toast_bg", "پیام‌های سایت — پس‌زمینه", "rgba(255,255,255,.9)", ".site-toast{background:{v}!important}"),
        Token("toast_text", "پیام‌های سایت — متن", "#1A1C1C", ".site-toast{color:{v}!important}"),
    ]),
    Group("shadow_colors", "🌘 رنگ سایه‌ها در تمام بخش‌های سایت",
          "رنگ سایه اجزای اصلی را مستقل تنظیم کنید. مقدار rgba برای کنترل شدت و شفافیت مناسب است؛ مثال rgba(9,38,52,.18). این تنظیمات فقط رنگ سایه را در خانواده مربوط تغییر می‌دهند.", [
        Token("shadow_surfaces", "سایه کارت‌ها و سطوح (کارت‌ها، پنل‌ها و باکس‌ها)", "rgba(7,29,43,.12)",
              ".glass-panel,.glass-card,.light-mini,.hero-card,.about-glass,.about-panel,.pd-aside,.pd-related-item,.article-card,.journal-card,.service-card,.contact-panel,.contact-details{box-shadow:0 18px 48px {v}!important}"),
        Token("shadow_buttons", "سایه دکمه‌ها (اصلی، شیشه‌ای، هدر و CTA)", "rgba(180,83,46,.28)",
              ".btn-primary,.btn-glass,.header-consult-btn,.g-cta,.pd-btn-primary,.pd-btn-glass,.pd-cta,.about-btn-copper,.about-btn-light,.more-btn{box-shadow:0 10px 28px {v}!important}"),
        Token("shadow_navigation", "سایه هدر و منوها", "rgba(7,29,43,.16)",
              ".site-header,.g-bar,.main-nav,.g-panel,.site-header .main-nav{box-shadow:0 14px 42px {v}!important}"),
        Token("shadow_project_cards", "سایه کارت‌ها و ردیف‌های پروژه", "rgba(7,29,43,.12)",
              ".mini-project,.mini-project:hover,.mini-project.project-preview,.proj-row,.proj-row:hover,.project-card,.featured-project,.pd-related-item{box-shadow:0 14px 38px {v}!important}"),
        Token("shadow_floating", "سایه دکمه‌های شناور", "rgba(7,29,43,.16)",
              ".floating-call,.pc-view{box-shadow:0 10px 30px {v}!important}"),
        Token("shadow_modal", "سایه پنجره‌ها و فرم‌ها", "rgba(7,29,43,.24)",
              ("#consultModal{--request-legacy-shadow:{v}}", ".site-toast{box-shadow:0 28px 80px {v}!important}")),
    ]),
]

RETIRED_DECORATIONS = frozenset({
    "header_border", "toggle_border", "card_btn_circle", "shadow_buttons", "shadow_navigation", "pd_btn_shadow", "pd_btn_pulse",
    "card_status_ongoing_dot", "card_status_completed_dot",
    "row_status_ongoing_dot", "row_status_completed_dot",
    "about_card_bg", "about_btn_main_bg", "about_btn_main_text",
    "header_cta_bg", "header_cta_hover", "header_cta_text", "all_btn_bg", "rail_nav_bg", "rail_nav_icon",
    "page_projects_bg", "page_project_detail_bg", "back_btn_bg", "back_btn_text",
    "text_section_link", "footer_contact_icon", "shadow_surfaces", "shadow_project_cards",
} | {token.key for group in GROUPS if group.key in {"projects_page", "project_detail"} for token in group.tokens})

ALL_TOKENS = [t for g in GROUPS for t in g.tokens]
ACTIVE_TOKENS = tuple(token for token in ALL_TOKENS if token.key not in RETIRED_DECORATIONS)
TOKENS_BY_KEY = {t.key: t for t in ALL_TOKENS}
MODAL_TOKENS = {token.key for group in GROUPS if group.key == "modal" for token in group.tokens}
# Keep saved colors from the older modal for rollback without applying them to the new controls.
LEGACY_MODAL_COLORS = frozenset({
    "modal_overlay", "modal_panel_bg", "modal_panel_solid", "modal_panel_border", "modal_shadow",
    "modal_line", "modal_title", "modal_subtitle", "modal_label", "modal_required", "modal_input_bg",
    "modal_input_border", "modal_input_text", "modal_placeholder", "modal_selected_bg", "modal_focus",
    "modal_error", "modal_submit_bg", "modal_submit_border", "modal_submit_text", "modal_submit_hover",
    "modal_close_bg", "modal_close_border", "modal_close_text", "modal_close_hover",
})

# ---- بررسی ساختار در زمان import: کلید تکراری یا مقدار پیش‌فرض نامعتبر = خطای سریع ----
assert len(TOKENS_BY_KEY) == len(ALL_TOKENS), "theme_tokens: duplicate token key"
for _t in ALL_TOKENS:
    assert _t.normalize(_t.default), "theme_tokens: invalid default for %s" % _t.key


def _prefix_selector(selector):
    selector = selector.strip()
    if selector.startswith("body"):
        return "html " + selector
    return "html body " + selector


def _render_rule(rule, value):
    selector_part, _, body = rule.partition("{")
    selectors = ",".join(_prefix_selector(s) for s in selector_part.split(","))
    return selectors + "{" + body.replace("{v}", value)


def clean_overrides(raw):
    """فقط کلیدهای شناخته‌شده با رنگ یا اندازهٔ معتبر نگه داشته می‌شوند."""
    cleaned = {}
    if isinstance(raw, dict):
        for key, value in raw.items():
            token = TOKENS_BY_KEY.get(key)
            if token:
                normalized = token.normalize(value)
            elif key in LEGACY_MODAL_COLORS:
                normalized = normalize_color(value)
            else:
                continue
            if normalized:
                cleaned[key] = normalized
    return cleaned


def build_theme_css(raw_overrides):
    """CSS نهایی تنظیمات ظاهری از قالب‌های ثابت و مقدارهای اعتبارسنجی‌شده."""
    overrides = clean_overrides(raw_overrides)
    chunks = []
    for token in ACTIVE_TOKENS:  # ترتیب ثابت = خروجی قابل پیش‌بینی
        value = overrides.get(token.key)
        if value is None and token.key in MODAL_TOKENS:
            value = token.default
            if token.key == "request_shadow":
                value = f"var(--request-legacy-shadow,{value})"
        if value is None:
            continue
        for rule in token.rules:
            chunks.append(_render_rule(rule, value))
    return "\n".join(chunks)
