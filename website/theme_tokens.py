"""
website/theme_tokens.py
وظیفه: فهرست مرکزی «رنگ‌های قابل تغییر اجزای سایت».

هر توکن = یک رنگ قابل ویرایش از پنل ادمین (پوسته و طراحی سایت).
- فقط مقدارهایی که مدیر سایت وارد کرده ذخیره می‌شوند؛ فیلد خالی یعنی «ظاهر پیش‌فرض».
- برای هر توکن‌ی که مقدار دارد، یک قانون CSS ساخته می‌شود؛ پس بدون مقدار هیچ چیز در ظاهر سایت تغییر نمی‌کند.
- مقدارها قبل از ذخیره و دوباره هنگام ساخت CSS با فهرست سفید (HEX / rgb / rgba / transparent) اعتبارسنجی
  می‌شوند؛ بنابراین هیچ متن دلخواهی وارد CSS نمی‌شود.
- این فایل عمداً Django را import نمی‌کند تا مستقل تست شود.

افزودن رنگ جدید: فقط یک خط Token به گروه مناسب اضافه کنید (کلید یکتا، برچسب، رنگ پیش‌فرض نمایشی، قانون/قوانین CSS).
در قانون CSS، {v} با مقدار رنگ جایگزین می‌شود.
"""
import re

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
    __slots__ = ("key", "label", "default", "rules")

    def __init__(self, key, label, default, rules):
        self.key = key
        self.label = label
        self.default = default
        self.rules = tuple(rules) if isinstance(rules, (list, tuple)) else (rules,)

    @property
    def field_name(self):
        return "c_" + self.key


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
        Token("page_bg", "پس‌زمینه کل سایت", "#F9F9F9", "body.site-shell{background:{v}!important}"),
        Token("sec_home_projects_bg", "بخش «گارنت، در یک نگاه» (کل پروژه‌ها) در صفحه اصلی", "#F6F3ED",
              ".section.home-projects{background:{v}!important}"),
        Token("sec_about_bg", "بخش «درباره گارنت» در صفحه اصلی (پشت کادر)", "#F6F3ED",
              ".section.about-lux-section{background:{v}!important}"),
        Token("sec_home_blog_bg", "بخش مقالات در صفحه اصلی", "#F9F9F9",
              ".section.home-blog{background:{v}!important}"),
        Token("page_projects_bg", "صفحه «پروژه‌ها» (لیست پروژه‌ها)", "#F6F3ED",
              ".section.projects-page{background:{v}!important}"),
        Token("page_project_detail_bg", "صفحه داخلی هر پروژه (بخش متن و اطلاعات)", "#F9F9F9",
              ".section.pd-body{background:{v}!important}"),
        Token("page_blog_list_bg", "صفحه «مقالات و اخبار» (لیست مقالات)", "#F9F9F9",
              ".section.blog-list-page{background:{v}!important}"),
        Token("page_blog_detail_bg", "صفحه داخلی هر مقاله", "#F9F9F9",
              ".section.blog-detail-page{background:{v}!important}"),
    ]),
    Group("texts", "🔤 رنگ تیترها و متن‌های عمومی", "تیتر بخش‌ها، لینک‌ها و متن‌های صفحه‌ها.", [
        Token("text_body", "متن عمومی سایت", "#1A1C1C", "body.site-shell{color:{v}!important}"),
        Token("text_heading", "تیتر بخش‌ها و صفحه‌ها",
              "#1A1C1C", ".compact-heading h1,.compact-heading h2,.compact-heading h3{color:{v}!important}"),
        Token("text_section_link", "لینک «همه مقالات» و لینک‌های کنار تیتر", "#092634",
              ".compact-heading .section-link{color:{v}!important}"),
        Token("text_empty_state", "پیام‌های خالی (مثل «پروژه‌ای ثبت نشده»)", "#60727D",
              ".empty-state,.projects-block .empty-state{color:{v}!important}"),
    ]),
    Group("header", "▣ هدر (نوار بالای سایت) و منوی دسکتاپ", "نوار شیشه‌ای بالای سایت، لینک‌های منو و دکمه مشاوره.", [
        Token("header_bg", "پس‌زمینه نوار هدر", "rgba(14,22,28,.5)",
              [".g-header .g-bar{background:{v}!important}", ".g-header.scrolled .g-bar{background:{v}!important}"]),
        Token("header_border", "خط دور نوار هدر", "rgba(255,255,255,.34)", ".g-header .g-bar{border-color:{v}!important}"),
        Token("header_link", "رنگ لینک‌های منو", "rgba(255,255,255,.86)",
              ".g-header .g-nav>a,.g-header .g-nav .g-nav-btn,.g-header .g-nav .g-nav-parent{color:{v}!important}"),
        Token("header_link_hover", "رنگ لینک منو هنگام نگه‌داشتن ماوس / صفحه فعال", "#FFFFFF",
              ".g-header .g-nav>a:hover,.g-header .g-nav>a.is-active,.g-header .g-nav .g-nav-parent:hover,.g-header .g-nav .g-nav-parent.is-active,.g-header .g-nav .g-nav-btn:hover,.g-header .g-nav .g-nav-btn:focus-visible,.g-header .g-nav .g-nav-group.is-open>.g-nav-parent{color:{v}!important}"),
        Token("header_underline", "خط زیر لینک فعال منو", "#FFFFFF",
              ".g-header .g-nav>a::after,.g-header .g-nav .g-nav-parent::after,.g-header .g-nav .g-nav-btn::after{background:{v}!important}"),
        Token("header_brand_text", "نام برند (وقتی لوگو آپلود نشده)", "#FFFFFF", ".g-header .g-brand .brand-text{color:{v}!important}"),
        Token("header_cta_bg", "دکمه «درخواست مشاوره» — پس‌زمینه", "#C0603A",
              ".g-header .g-cta{background:{v}!important;background-image:none!important}"),
        Token("header_cta_hover", "دکمه «درخواست مشاوره» — پس‌زمینه هنگام Hover", "#D2693F",
              ".g-header .g-cta:hover{background:{v}!important;background-image:none!important;filter:none!important}"),
        Token("header_cta_text", "دکمه «درخواست مشاوره» — رنگ متن", "#FFFFFF", ".g-header .g-cta,.g-header .g-cta span{color:{v}!important}"),
        Token("header_cta_border", "دکمه «درخواست مشاوره» — رنگ لبه", "rgba(255,255,255,.2)", ".g-header .g-cta{border-color:{v}!important}"),
        Token("header_dropdown_bg", "زیرمنوی پروژه‌ها (دسکتاپ) — پس‌زمینه", "rgba(12,20,26,.9)", ".g-header .g-sub{background:{v}!important}"),
        Token("header_dropdown_border", "زیرمنوی پروژه‌ها (دسکتاپ) — لبه", "rgba(255,255,255,.28)", ".g-header .g-sub{border-color:{v}!important}"),
        Token("header_dropdown_text", "زیرمنوی پروژه‌ها (دسکتاپ) — متن", "#FFFFFF", ".g-header .g-sub a{color:{v}!important}"),
        Token("header_dropdown_hover", "زیرمنوی پروژه‌ها (دسکتاپ) — پس‌زمینه گزینه هنگام Hover", "rgba(255,255,255,.16)",
              ".g-header .g-sub a:hover,.g-header .g-sub a:focus-visible{background:{v}!important}"),
    ]),
    Group("mobile_menu", "☰ منوی موبایل (دکمه سه‌خط و پنل باز شونده)", "ظاهر منو در موبایل و تبلت.", [
        Token("toggle_lines", "رنگ سه‌خط منو (همبرگری)", "#FFFFFF", ".g-header .g-toggle span{background:{v}!important}"),
        Token("toggle_bg", "پس‌زمینه دکمه سه‌خط", "rgba(255,255,255,.08)", ".g-header .g-toggle{background:{v}!important}"),
        Token("toggle_border", "لبه دکمه سه‌خط", "rgba(255,255,255,.18)", ".g-header .g-toggle{border-color:{v}!important}"),
        Token("panel_bg", "پس‌زمینه پنل منو", "rgba(12,20,26,.82)", ".g-header .g-panel{background:{v}!important}"),
        Token("panel_border", "لبه پنل منو", "rgba(255,255,255,.28)", ".g-header .g-panel{border-color:{v}!important}"),
        Token("panel_item_bg", "پس‌زمینه گزینه‌های پنل", "rgba(255,255,255,.06)",
              ".g-header .g-panel a,.g-header .g-panel .g-panel-btn{background:{v}!important}"),
        Token("panel_item_hover", "گزینه‌های پنل هنگام لمس / فعال", "rgba(255,255,255,.16)",
              ".g-header .g-panel a:hover,.g-header .g-panel a.is-active,.g-header .g-panel .g-panel-btn:hover{background:{v}!important}"),
        Token("panel_item_text", "متن گزینه‌های پنل", "#FFFFFF",
              ".g-header .g-panel a,.g-header .g-panel .g-panel-btn{color:{v}!important}"),
        Token("panel_sub_bg", "زیرگزینه‌های پروژه‌ها در پنل — پس‌زمینه", "rgba(255,255,255,.1)", ".g-header .g-panel .g-panel-sub a{background:{v}!important}"),
    ]),
    Group("hero", "🎬 بخش اصلی (Hero) صفحه اصلی", "تیتر، توضیح و دکمه‌های روی تصویر/ویدیوی اول صفحه.", [
        Token("hero_title", "تیتر اصلی", "#FFFFFF", ".hero h1{color:{v}!important}"),
        Token("hero_text", "متن زیر تیتر", "rgba(255,255,255,.78)", ".hero .hero-copy>p{color:{v}!important}"),
        Token("hero_btn_text", "متن دکمه‌های شیشه‌ای Hero", "#FFFFFF", ".hero .hero-glass-action{color:{v}!important}"),
        Token("hero_btn_hover", "دکمه‌های Hero هنگام Hover", "rgba(255,255,255,.17)", ".hero .hero-glass-action:hover{background:{v}!important}"),
    ]),
    Group("preview_cards", "🏗️ کارت‌های پیش‌نمایش پروژه و مقاله (صفحه اصلی، جزئیات پروژه، لیست مقالات)",
          "کارت‌هایی که روی تصویر نوشته دارند؛ شامل وضعیت، عنوان، موقعیت و دکمه‌ی مشاهده.", [
        Token("card_bg", "زمینه کارت (پشت تصویر / وقتی تصویر ندارد) — هماهنگ با بخش درباره گارنت", "#F6F3ED",
              ".mini-project.project-preview{background:{v}!important;background-image:none!important}"),
        Token("card_shadow", "سایه کارت‌های پیش‌نمایش (برای حذف سایه rgba(0,0,0,0) وارد کنید)", "rgba(0,0,0,0)",
              ".mini-project.project-preview,.mini-project.project-preview:hover{box-shadow:0 12px 28px {v}!important}"),
        Token("card_title", "عنوان روی کارت", "#FFFFFF", ".mini-project.project-preview .pc-bottom h3{color:{v}!important}"),
        Token("card_location", "موقعیت / تاریخ روی کارت", "#FFFFFF", ".mini-project.project-preview .pc-loc{color:{v}!important}"),
        Token("card_status_ongoing_bg", "نشان «در حال اجرا» — پس‌زمینه", "rgba(34,70,58,.5)", ".mini-project.project-preview .pc-status.pc-ongoing{background:{v}!important}"),
        Token("card_status_ongoing_dot", "نشان «در حال اجرا» — نقطه", "#2CF08A", ".mini-project.project-preview .pc-status.pc-ongoing i{background:{v}!important;box-shadow:0 0 9px {v}!important}"),
        Token("card_status_completed_bg", "نشان «به اتمام رسیده» — پس‌زمینه", "rgba(30,52,82,.5)", ".mini-project.project-preview .pc-status.pc-completed{background:{v}!important}"),
        Token("card_status_completed_dot", "نشان «به اتمام رسیده» — نقطه", "#7CC4FF", ".mini-project.project-preview .pc-status.pc-completed i{background:{v}!important;box-shadow:0 0 9px {v}!important}"),
        Token("card_status_text", "متن نشان وضعیت / دسته مقاله", "#FFFFFF", ".mini-project.project-preview .pc-status{color:{v}!important}"),
        Token("card_btn_bg", "دکمه «مشاهده» — پس‌زمینه", "rgba(244,249,252,.94)", ".mini-project.project-preview .pc-view{background:{v}!important}"),
        Token("card_btn_text", "دکمه «مشاهده» — متن و فلش", "#071D2B",
              ".mini-project.project-preview .pc-view,.mini-project.project-preview .pc-view span,.mini-project.project-preview .pc-view em,.mini-project.project-preview .pc-view svg{color:{v}!important;stroke:{v}!important}"),
        Token("card_btn_circle", "دایره‌ی فلش در دکمه «مشاهده»", "#FFFFFF", ".mini-project.project-preview .pc-view em{background:{v}!important}"),
    ]),
    Group("rail_buttons", "⏩ دکمه‌های ردیف پروژه‌ها", "دکمه‌ی گرد «مشاهده همه پروژه‌ها» و فلش‌های چپ/راست ردیف چرخان.", [
        Token("all_btn_bg", "دکمه‌ی آیکونی «مشاهده همه پروژه‌ها» — پس‌زمینه", "#FF6E42",
              ".all-projects-btn{background:{v}!important;background-image:none!important}"),
        Token("all_btn_icon", "دکمه‌ی آیکونی «مشاهده همه پروژه‌ها» — آیکون", "#FFFFFF", ".all-projects-btn{color:{v}!important}"),
        Token("rail_nav_bg", "فلش‌های چپ/راست ردیف — پس‌زمینه", "rgba(255,255,255,.94)", ".rail-nav{background:{v}!important}"),
        Token("rail_nav_icon", "فلش‌های چپ/راست ردیف — آیکون", "#071D2B", ".rail-nav{color:{v}!important}"),
    ]),
    Group("about", "🏛️ بخش «درباره گارنت» (کادر شیشه‌ای)", "کادر، متن و دکمه‌های درباره گارنت در صفحه اصلی.", [
        Token("about_card_bg", "پس‌زمینه کادر", "rgba(255,255,255,.88)",
              [".about-glass,.about-glass:not(:has(.about-bg)){background:{v}!important}", ".about-glass::before{display:none!important}"]),
        Token("about_card_border", "لبه کادر", "rgba(255,255,255,.75)", ".about-glass{border-color:{v}!important}"),
        Token("about_title", "عنوان", "#092634", ".about-panel h2{color:{v}!important}"),
        Token("about_text", "متن", "#27414F", ".about-panel .about-text,.about-panel .about-text p{color:{v}!important}"),
        Token("about_btn_main_bg", "دکمه «مشاهده پروژه‌ها» — پس‌زمینه", "#CC6D44", ".about-btn.about-btn-copper{background:{v}!important;background-image:none!important}"),
        Token("about_btn_main_text", "دکمه «مشاهده پروژه‌ها» — متن", "#FFFFFF", ".about-btn.about-btn-copper{color:{v}!important}"),
        Token("about_btn_light_bg", "دکمه «درخواست مشاوره» — پس‌زمینه", "rgba(255,255,255,.75)", ".about-btn.about-btn-light{background:{v}!important}"),
        Token("about_btn_light_text", "دکمه «درخواست مشاوره» — متن", "#092634", ".about-btn.about-btn-light{color:{v}!important}"),
    ]),
    Group("projects_page", "📋 صفحه «پروژه‌ها» (لیست پروژه‌ها)", "انتخاب‌گرها، تیتر بخش‌ها و ردیف‌های لیست پروژه.", [
        Token("tabs_bg", "کپسول‌های «در حال اجرا / تمام شده» — پس‌زمینه", "#FFFFFF", ".projects-tabs a{background:{v}!important}"),
        Token("tabs_text", "کپسول‌های «در حال اجرا / تمام شده» — متن", "#0B2A3A", ".projects-tabs a{color:{v}!important}"),
        Token("tabs_count_bg", "شمارنده کپسول‌ها", "#0B2A3A", ".projects-tabs b{background:{v}!important}"),
        Token("block_heading", "تیتر هر گروه (پروژه‌های در حال اجرا / اتمام شده)", "#0B2A3A", ".projects-block-head h2{color:{v}!important}"),
        Token("row_bg", "ردیف پروژه — پس‌زمینه", "#FFFFFF", ".proj-row{background:{v}!important}"),
        Token("row_shadow", "سایه ردیف پروژه (برای حذف سایه rgba(0,0,0,0) وارد کنید)", "rgba(0,0,0,0)", ".proj-row,.proj-row:hover{box-shadow:0 18px 44px {v}!important}"),
        Token("row_border", "ردیف پروژه — لبه", "rgba(9,38,52,.1)", ".proj-row{border-color:{v}!important}"),
        Token("row_title", "ردیف پروژه — عنوان", "#0B2A3A", ".proj-row .proj-row-title{color:{v}!important}"),
        Token("row_text", "ردیف پروژه — توضیح", "#4B6370", ".proj-row .proj-row-desc{color:{v}!important}"),
        Token("row_meta", "ردیف پروژه — موقعیت و اطلاعات", "#60727D", ".proj-row .proj-row-meta,.proj-row .proj-row-meta span{color:{v}!important}"),
        Token("row_btn_bg", "ردیف پروژه — دکمه مشاهده", "#0B2A3A", ".proj-row .proj-row-btn{background:{v}!important}"),
        Token("row_btn_text", "ردیف پروژه — متن دکمه مشاهده", "#FFFFFF", ".proj-row .proj-row-btn,.proj-row .proj-row-btn span,.proj-row .proj-row-btn svg{color:{v}!important}"),
        Token("row_status_ongoing", "ردیف پروژه — نشان «در حال اجرا»", "#14804A",
              ".proj-row .proj-row-status.ps-ongoing{color:{v}!important;border-color:{v}!important}"),
        Token("row_status_ongoing_dot", "ردیف پروژه — نقطه‌ی «در حال اجرا»", "#2CF08A",
              ".proj-row .proj-row-status.ps-ongoing i{background:{v}!important;box-shadow:0 0 9px {v}!important}"),
        Token("row_status_completed", "ردیف پروژه — نشان «به اتمام رسیده»", "#1F5F93",
              ".proj-row .proj-row-status.ps-completed{color:{v}!important;border-color:{v}!important}"),
        Token("row_status_completed_dot", "ردیف پروژه — نقطه‌ی «به اتمام رسیده»", "#7CC4FF",
              ".proj-row .proj-row-status.ps-completed i{background:{v}!important;box-shadow:0 0 9px {v}!important}"),
        Token("row_badge_bg", "ردیف پروژه — نشان ویژه روی تصویر", "#FF6E42", ".proj-row .proj-row-badge{background:{v}!important}"),
    ]),
    Group("project_detail", "🏠 صفحه داخلی پروژه", "کادر اطلاعات، متن و دکمه‌های داخل هر پروژه.", [
        Token("pd_story_title", "عنوان متن پروژه", "#1A1C1C", ".pd-story h2{color:{v}!important}"),
        Token("pd_text", "متن معرفی پروژه", "#425661", ".pd-text p{color:{v}!important}"),
        Token("pd_aside_bg", "کادر «اطلاعات پروژه» — پس‌زمینه", "#FFFFFF", ".pd-aside{background:{v}!important}"),
        Token("pd_aside_border", "کادر «اطلاعات پروژه» — لبه", "rgba(7,29,43,.08)", ".pd-aside{border-color:{v}!important}"),
        Token("pd_aside_title", "کادر «اطلاعات پروژه» — عنوان", "#0B2A3A", ".pd-aside h3{color:{v}!important}"),
        Token("pd_aside_text", "کادر «اطلاعات پروژه» — متن", "#33474F", ".pd-features li{color:{v}!important}"),
        Token("pd_btn_main_bg", "دکمه بالای صفحه پروژه (مشاوره) — پس‌زمینه", "#CC6C42", ".pd-btn.pd-btn-primary{background:{v}!important;background-image:none!important}"),
        Token("pd_btn_glass_bg", "دکمه شیشه‌ای (گالری) — پس‌زمینه", "rgba(255,255,255,.13)", ".pd-btn.pd-btn-glass{background:{v}!important}"),
        Token("pd_btn_text", "متن دکمه‌های بالای صفحه پروژه", "#FFFFFF", ".pd-btn,.pd-btn .pd-btn-label{color:{v}!important}"),
        Token("pd_chip_bg", "کپسول‌های کد / وضعیت / سال", "rgba(20,26,30,.28)", ".pd-chips li{background:{v}!important}"),
    ]),
    Group("blog_pages", "📰 صفحات مقالات و اخبار", "متن و تیترهای صفحه داخلی مقاله.", [
        Token("article_title", "تیتر مقاله", "#1A1C1C", ".article-shell h1{color:{v}!important}"),
        Token("article_text", "متن مقاله", "#425661", ".article-content,.article-content p{color:{v}!important}"),
        Token("article_meta", "تاریخ انتشار", "#73838A", ".article-meta,.article-meta span{color:{v}!important}"),
    ]),
    Group("footer", "⬛ فوتر (پایین سایت)", "رنگ زمینه، تیترها، لینک‌ها، آیکون‌ها و فرم خبرنامه.", [
        Token("footer_bg", "پس‌زمینه فوتر", "#000000", ".site-footer{background:{v}!important;background-image:none!important}"),
        Token("footer_text", "متن‌های فوتر", "#FFFFFF", ".site-footer{color:{v}!important}"),
        Token("footer_heading", "تیترهای ستون‌های فوتر", "#FFFFFF", ".site-footer .footer-col h4{color:{v}!important}"),
        Token("footer_link", "لینک‌ها و متن ستون‌ها", "rgba(255,255,255,.66)",
              ".site-footer .footer-grid-reference .footer-col>a,.site-footer .footer-grid-reference .footer-col>p,.site-footer .footer-text-button{color:{v}!important}"),
        Token("footer_link_hover", "لینک‌ها هنگام Hover", "#FFFFFF",
              ".site-footer .footer-grid-reference .footer-col>a:hover,.site-footer .footer-text-button:hover{color:{v}!important}"),
        Token("footer_contact_icon", "آیکون تلفن و ایمیل", "#39BD80", ".site-footer .footer-contact-icon{color:{v}!important}"),
        Token("footer_social", "آیکون‌های اینستاگرام و لینکدین", "#FFFFFF", ".site-footer .footer-social-links a{color:{v}!important}"),
        Token("footer_news_bg", "فرم خبرنامه — پس‌زمینه", "#FFFFFF", ".site-footer .newsletter-form{background:{v}!important}"),
        Token("footer_news_text", "فرم خبرنامه — رنگ متن ایمیل", "#192A35", ".site-footer .newsletter-form input[type=email]{color:{v}!important}"),
        Token("footer_news_btn", "فرم خبرنامه — دکمه ثبت", "#35C878", ".site-footer .newsletter-form button{background:{v}!important}"),
        Token("footer_bottom_text", "نوار پایین فوتر (کپی‌رایت و بازگشت به بالا)", "rgba(255,255,255,.66)", ".site-footer .footer-bottom,.site-footer .footer-bottom span,.site-footer .footer-bottom a{color:{v}!important}"),
        Token("footer_bottom_line", "خط بالای نوار پایین فوتر", "rgba(255,255,255,.09)", ".site-footer .footer-bottom{border-top-color:{v}!important}"),
    ]),
    Group("modal", "📝 پاپ‌آپ فرم درخواست مشاوره", "پنجره‌ی باز شونده‌ی فرم مشاوره.", [
        Token("modal_overlay", "پرده‌ی پشت فرم", "rgba(7,29,43,.48)", "#consultModal.is-open:not([hidden]){background:{v}!important}"),
        Token("modal_panel_bg", "پس‌زمینه کادر فرم", "rgba(248,249,248,.9)", "#consultModal.is-open:not([hidden])>.consult-modal-inner{background:{v}!important}"),
        Token("modal_panel_border", "لبه کادر فرم", "rgba(255,255,255,.96)", "#consultModal.is-open:not([hidden])>.consult-modal-inner{border-color:{v}!important}"),
        Token("modal_title", "تیتر فرم", "#092634", "#consultModal .modal-heading h2{color:{v}!important}"),
        Token("modal_subtitle", "توضیح زیر تیتر", "#64757D", "#consultModal .modal-heading p{color:{v}!important}"),
        Token("modal_label", "عنوان فیلدها", "#244754", "#consultModal label{color:{v}!important}"),
        Token("modal_input_bg", "فیلدهای ورودی — پس‌زمینه", "rgba(255,255,255,.57)", "#consultModal .form-control{background:{v}!important}"),
        Token("modal_input_text", "فیلدهای ورودی — متن", "#17303B", "#consultModal .form-control{color:{v}!important}"),
        Token("modal_submit_bg", "دکمه «ثبت درخواست» — پس‌زمینه", "#FF6E42", "#consultModal .btn.btn-primary{background:{v}!important}"),
        Token("modal_submit_text", "دکمه «ثبت درخواست» — متن", "#081923", "#consultModal .btn.btn-primary{color:{v}!important}"),
        Token("modal_close_bg", "دکمه بستن (×)", "rgba(255,255,255,.65)", "#consultModal .modal-close{background:{v}!important}"),
    ]),
    Group("floating", "🔘 دکمه‌های شناور و پیام‌ها", "دکمه‌ی گرد تماس، دکمه‌ی «بازگشت» و پیام‌های موفقیت/خطا.", [
        Token("float_call_bg", "دکمه گرد تماس — پس‌زمینه", "#FF6E42", ".floating-call{background:{v}!important;background-image:none!important}"),
        Token("float_call_icon", "دکمه گرد تماس — آیکون", "#FFFFFF", ".floating-call{color:{v}!important}"),
        Token("back_btn_bg", "دکمه «بازگشت» — پس‌زمینه", "rgba(255,255,255,.9)", ".mobile-back{background:{v}!important}"),
        Token("back_btn_text", "دکمه «بازگشت» — متن", "#092634", ".mobile-back,.mobile-back b{color:{v}!important}"),
        Token("toast_bg", "پیام‌های سایت — پس‌زمینه", "rgba(255,255,255,.9)", ".site-toast{background:{v}!important}"),
        Token("toast_text", "پیام‌های سایت — متن", "#1A1C1C", ".site-toast{color:{v}!important}"),
    ]),
]

ALL_TOKENS = [t for g in GROUPS for t in g.tokens]
TOKENS_BY_KEY = {t.key: t for t in ALL_TOKENS}

# ---- بررسی ساختار در زمان import: کلید تکراری یا مقدار پیش‌فرض نامعتبر = خطای سریع ----
assert len(TOKENS_BY_KEY) == len(ALL_TOKENS), "theme_tokens: duplicate token key"
for _t in ALL_TOKENS:
    assert normalize_color(_t.default), "theme_tokens: invalid default for %s" % _t.key


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
    """فقط کلیدهای شناخته‌شده با مقدار معتبر نگه داشته می‌شوند."""
    cleaned = {}
    if isinstance(raw, dict):
        for key, value in raw.items():
            token = TOKENS_BY_KEY.get(key)
            normalized = normalize_color(value) if token else None
            if normalized:
                cleaned[key] = normalized
    return cleaned


def build_theme_css(raw_overrides):
    """CSS نهایی رنگ‌های تغییرداده‌شده؛ خروجی فقط از قالب‌های ثابت این فایل و مقدارهای اعتبارسنجی‌شده ساخته می‌شود."""
    overrides = clean_overrides(raw_overrides)
    chunks = []
    for token in ALL_TOKENS:  # ترتیب ثابت = خروجی قابل پیش‌بینی
        value = overrides.get(token.key)
        if not value:
            continue
        for rule in token.rules:
            chunks.append(_render_rule(rule, value))
    return "\n".join(chunks)
