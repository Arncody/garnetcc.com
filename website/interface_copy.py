"""Shared bilingual interface labels. Page and project records own their content."""

COPY_GROUPS = {
    "پوسته و سربرگ": (
        ("skip_content", "پرش به محتوا", "رفتن به محتوای اصلی", "Skip to content"),
        ("nav_main", "عنوان منوی اصلی", "منوی اصلی", "Main"),
        ("nav_menu", "عنوان منوی موبایل", "منو", "Menu"),
        ("call_label", "عنوان دکمه تماس", "تماس با گارنت", "Call Garnet"),
        ("home_title_suffix", "عنوان پیش‌فرض صفحه اصلی", "معماری و ساخت لوکس", "Luxury Architecture & Development"),
    ),
    "صفحه اصلی و پرتفولیو": (
        ("company_catalog", "دکمه کاتالوگ شرکت", "کاتالوگ شرکت", "Company catalog"),
        ("home_ongoing", "دکمه پیش‌فرض پروژه‌های در حال اجرا در اول صفحه", "پروژه‌های در حال اجرا", "Ongoing Projects"),
        ("home_completed", "دکمه پیش‌فرض پروژه‌های تکمیل‌شده در اول صفحه", "پروژه‌های تکمیل‌شده", "Completed Projects"),
        ("home_empty", "پیام خالی پیش‌نمایش پروژه‌ها", "پروژه‌ها در این بخش نمایش داده می‌شوند.", "Projects will appear here."),
        ("portfolio_title", "عنوان پیش‌فرض پرتفولیو", "پروژه‌های گارنت", "Garnet Projects"),
        ("portfolio_kicker", "برچسب پیش‌فرض پرتفولیو", "GARNET / PORTFOLIO", "GARNET / PORTFOLIO"),
        ("project_collection", "لینک بازدید فهرست", "پروژه‌ها", "Projects"),
        ("project_status", "عنوان وضعیت", "وضعیت پروژه", "Status"),
        ("status_ongoing", "نشان در حال اجرا", "در حال اجرا", "In progress"),
        ("status_completed", "نشان تکمیل‌شده", "تکمیل‌شده", "Completed"),
        ("no_ongoing", "پیام خالی پروژه‌های در حال اجرا", "فعلاً پروژهٔ در حال اجرایی ثبت نشده است.", "No ongoing projects yet."),
        ("no_completed", "پیام خالی پروژه‌های تکمیل‌شده", "فعلاً پروژهٔ تکمیل‌شده‌ای ثبت نشده است.", "No completed projects yet."),
        ("project_results", "عنوان تعداد نتایج", "تعداد نتایج", "Results"),
        ("project_no_matches", "پیام بدون نتیجه", "پروژه‌ای مطابق جست‌وجو پیدا نشد.", "No matching projects found."),
        ("project_clear_search", "پیوند پاک‌کردن جست‌وجو", "پاک‌کردن جست‌وجو", "Clear search"),
    ),
    "جزئیات پروژه و گالری": (
        ("project_code", "عنوان کد پروژه", "کد پروژه", "Project code"),
        ("project_location", "عنوان موقعیت", "موقعیت", "Location"),
        ("project_year", "عنوان سال", "سال", "Year"),
        ("project_progress", "عنوان پیشرفت اجرایی", "پیشرفت اجرایی", "Construction progress"),
        ("project_current_stage", "عنوان مرحله فعلی", "مرحلهٔ فعلی", "Current stage"),
        ("gallery_enlarge", "برچسب بزرگ‌نمایی", "بزرگ‌نمایی", "Enlarge"),
        ("gallery_collapse", "برچسب کوچک‌کردن عکس", "کوچک‌کردن عکس", "Collapse photo"),
        ("gallery_of", "جداکننده شمارنده عکس", "از", "of"),
        ("gallery_help", "راهنمای حرکت در نمایشگر", "برای جابه‌جایی، از فلش‌ها یا کلیدهای جهت‌دار استفاده کنید یا عکس را بکشید.", "Use the arrow buttons or keys, swipe, or drag the photo to browse."),
        ("gallery_previous", "عنوان عکس قبلی", "عکس قبلی", "Previous photo"),
        ("gallery_next", "عنوان عکس بعدی", "عکس بعدی", "Next photo"),
        ("close_label", "عنوان بستن پنجره", "بستن", "Close"),
    ),
    "فوتر و خبرنامه": (
        ("footer_quick", "عنوان دسترسی سریع", "دسترسی سریع", "Quick links"),
        ("footer_about", "عنوان ستون درباره", "درباره گارنت", "About Garnet"),
        ("footer_company", "پیوند معرفی شرکت", "معرفی شرکت", "About the company"),
        ("footer_contact", "عنوان ستون ارتباط", "ارتباط با ما", "Contact us"),
        ("footer_subscribe_title", "عنوان ستون خبرنامه", "خبرنامه و شبکه‌های اجتماعی", "Newsletter and social media"),
        ("footer_subscribe_note", "توضیح خبرنامه", "برای دریافت خبرها و تازه‌های گارنت ایمیل خود را ثبت کنید", "Subscribe to receive our updates"),
        ("footer_email", "برچسب و راهنمای فیلد ایمیل", "آدرس ایمیل", "Email address"),
        ("footer_subscribe", "دکمه عضویت", "عضویت", "Subscribe"),
        ("footer_rights", "متن حقوق نشر", "تمامی حقوق محفوظ است.", "All rights reserved."),
        ("footer_language", "پیوند زبان دیگر", "English", "فارسی"),
        ("newsletter_success", "تأیید عضویت", "ایمیل شما با موفقیت در خبرنامه ثبت شد.", "Your email has been subscribed successfully."),
        ("newsletter_exists", "پیام ایمیل تکراری", "این ایمیل قبلاً در خبرنامه ثبت شده است.", "This email is already subscribed."),
        ("newsletter_invalid", "خطای ایمیل", "لطفاً یک آدرس ایمیل معتبر وارد کنید.", "Please enter a valid email address."),
        ("newsletter_limit", "محدودیت عضویت خبرنامه", "تعداد تلاش‌ها زیاد است؛ لطفاً کمی بعد دوباره امتحان کنید.", "Too many attempts. Please try again later."),
    ),
    "بازخورد فرم درخواست": (
        ("request_name_error", "خطای نام", "لطفاً نام و نام‌خانوادگی را وارد کنید.", "Please enter your full name."),
        ("request_phone_error", "خطای شماره", "لطفاً یک شماره تماس معتبر وارد کنید.", "Please enter a valid phone number."),
        ("request_gender_error", "خطای انتخاب عنوان", "لطفاً یکی از گزینه‌ها را انتخاب کنید.", "Please choose an option."),
        ("request_subject_error", "خطای موضوع", "لطفاً موضوع درخواست را وارد کنید.", "Please enter the subject of your request."),
        ("request_invalid", "خطای فرم", "لطفاً خطاهای فرم را برطرف کنید.", "Please correct the form errors."),
        ("request_limit", "محدودیت ارسال درخواست", "تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً کمی بعد دوباره تلاش کنید.", "Too many requests. Please try again later."),
        ("request_success", "تأیید ثبت درخواست", "درخواست مشاوره شما با موفقیت ثبت شد. به‌زودی با شما تماس می‌گیریم.", "Your request has been submitted. We will contact you soon."),
    ),
}

COPY_DEFAULTS = {key: (fa, en) for fields in COPY_GROUPS.values() for key, _, fa, en in fields}


def resolve_copy(overrides, lang):
    overrides = overrides if isinstance(overrides, dict) else {}
    return {
        key: _text(overrides.get(f"{key}_{lang}")) or defaults[lang == "en"]
        for key, defaults in COPY_DEFAULTS.items()
    }


def _text(value):
    return value.strip() if isinstance(value, str) else ""
