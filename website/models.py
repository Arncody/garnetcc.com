"""
website/models.py
وظیفه: تعریف تمام مدل‌های داده‌ای سایت گارنت.
هر مدل با یک دلیل مشخص طراحی شده و از پیچیدگی غیرضروری (مثل ذخیره HTML خام
یا JSON Builder) خودداری شده است. تمام محتوای قابل مشاهده در فرانت از همین
مدل‌ها می‌آید تا مدیر سایت بتواند همه‌چیز را از پنل ادمین ویرایش کند.
"""
from django.core.validators import RegexValidator, FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError
from django.db import models
from django.urls import reverse
from django.utils import timezone

phone_validator = RegexValidator(
    regex=r"^0(9\d{9}|\d{2,3}\d{7,8})$",
    message="شماره تماس معتبر وارد کنید (مثال: 09123456789 یا 02634019271).",
)

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 20 * 1024 * 1024
MAX_PDF_SIZE = 20 * 1024 * 1024

def validate_real_image(upload):
    """Check size and decode the file; extension and browser MIME alone are untrusted."""
    if upload.size > MAX_IMAGE_SIZE:
        raise ValidationError("حجم تصویر نباید بیشتر از ۱۰ مگابایت باشد.")
    try:
        position = upload.tell()
        upload.seek(0)
        image = Image.open(upload)
        if image.format not in {"JPEG", "PNG", "WEBP"}:
            raise ValidationError("فرمت واقعی تصویر باید JPG، PNG یا WebP باشد.")
        image.verify()
        upload.seek(position)
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise ValidationError("فایل تصویر معتبر نیست یا آسیب دیده است.")
    finally:
        try:
            upload.seek(0)
        except (AttributeError, OSError):
            pass

def validate_pdf(upload):
    if upload.size > MAX_PDF_SIZE:
        raise ValidationError("حجم PDF نباید بیشتر از ۲۰ مگابایت باشد.")
    position = upload.tell()
    upload.seek(0)
    signature = upload.read(5)
    upload.seek(position)
    if signature != b"%PDF-":
        raise ValidationError("فایل باید PDF معتبر باشد.")

def validate_video(upload):
    if upload.size > MAX_VIDEO_SIZE:
        raise ValidationError("حجم ویدیو نباید بیشتر از ۲۰ مگابایت باشد.")
    position = upload.tell()
    upload.seek(0)
    header = upload.read(16)
    upload.seek(position)
    # MP4/MOV use an ISO-BMFF 'ftyp' box; WebM uses EBML magic.
    if not (len(header) >= 8 and header[4:8] == b"ftyp") and not header.startswith(b"\\x1a\\x45\\xdf\\xa3"):
        raise ValidationError("امضای فایل ویدیو معتبر نیست؛ MP4/MOV یا WebM بارگذاری کنید.")

IMAGE_VALIDATORS = [
    FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
    validate_real_image,
]
VIDEO_VALIDATORS = [
    FileExtensionValidator(allowed_extensions=["mp4", "webm", "mov", "m4v"]),
    validate_video,
]
PDF_VALIDATORS = [FileExtensionValidator(allowed_extensions=["pdf"]), validate_pdf]


class SingletonModel(models.Model):
    """
    پایه‌ای برای مدل‌هایی که باید فقط یک رکورد از آن‌ها در سایت وجود داشته باشد
    (مثل تنظیمات کلی سایت یا بخش Hero). از پیچیدگی اضافه جلوگیری می‌کند.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # حذف تنظیمات اصلی سایت مجاز نیست

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    """اطلاعات کلی و ثابت شرکت که در سراسر سایت (Header/Footer/Contact) استفاده می‌شود."""

    brand_name = models.CharField("نام برند", max_length=100, default="گارنت")
    legal_name = models.CharField("نام حقوقی", max_length=200, default="بهمن ساختار آوید")
    logo = models.ImageField(
        "لوگو (ترکیبی: نماد + نام شرکت)", upload_to="site/", validators=IMAGE_VALIDATORS, blank=True,
        help_text="لوگوی کامل شرکت را آپلود کنید؛ به‌تنهایی (بدون متن جداگانه) در هدر و فوتر نمایش داده می‌شود. در نبود لوگو، نام برند نوشته می‌شود.",
    )
    logo_light = models.ImageField(
        "لوگوی نسخه روشن برای هدر (اختیاری)", upload_to="site/", validators=IMAGE_VALIDATORS, blank=True,
        help_text="هدر سایت شیشه‌ای و تیره است؛ اگر متن لوگوی شما تیره است، نسخه‌ای با متن سفید/روشن اینجا آپلود کنید. در نبود آن، همان لوگوی اصلی نمایش داده می‌شود.",
    )
    favicon = models.ImageField(
        "فاویکون (آیکون تب مرورگر و گوگل)", upload_to="site/", validators=IMAGE_VALIDATORS, blank=True,
        help_text="فقط نماد/آرم شرکت (بدون نوشته) به‌صورت مربع، PNG، حداقل 512×512 پیکسل. گوگل فقط آیکون‌های مربعی با اندازه مضرب 48 پیکسل را نمایش می‌دهد.",
    )
    tagline_en = models.CharField("Tagline (EN)", max_length=250, blank=True)
    tagline = models.CharField(
        "شعار کوتاه شرکت", max_length=250, blank=True,
        default="«گارنت» با پشتوانه رسمی شرکت بهمن ساختار آوید؛ در طراحی و اجرای آپارتمان‌های مدرن و فاخر مسکونی با تکیه بر اصالت مهندسی و سادگی معاصر.",
    )

    phone = models.CharField("شماره تماس", max_length=20, validators=[phone_validator], default="02634019271")
    email = models.EmailField("ایمیل", default="garnet-group3@gmail.com")
    address = models.TextField(
        "آدرس دفتر",
        default="البرز، کرج، گوهردشت، بلوار اصلی، مجتمع تجاری اداری نیکامال",
    )
    instagram_url = models.URLField("لینک اینستاگرام", default="https://instagram.com/garnet_cc", blank=True)
    linkedin_url = models.URLField(
        "لینک لینکدین", blank=True, default="",
        help_text="در فوتر سایت کنار اینستاگرام نمایش داده می‌شود؛ اگر خالی بماند، نمایش داده نمی‌شود.",
    )
    projects_carousel_enabled = models.BooleanField(
        "چرخش افقی خودکار پروژه‌ها", default=True,
        help_text="اگر خاموش شود، پروژه‌ها به‌صورت ردیف/شبکه‌ی ثابت نمایش داده می‌شوند.",
    )
    projects_carousel_speed = models.PositiveIntegerField(
        "سرعت چرخش پروژه‌ها (پیکسل بر ثانیه)", default=40,
        validators=[MinValueValidator(10), MaxValueValidator(200)],
        help_text="عدد بین ۱۰ تا ۲۰۰؛ مقدار استاندارد ۴۰ است (بزرگ‌تر = سریع‌تر).",
    )
    projects_carousel_on_list = models.BooleanField(
        "چرخش پروژه‌ها در صفحه «پروژه‌ها» هم اعمال شود", default=True,
    )

    booking_url = models.CharField(
        "لینک دکمه «هماهنگی جلسه»", max_length=200, blank=True, default="#contact",
        help_text="می‌تواند لینک تقویم رزرو یا لنگر داخلی صفحه (مثل #contact) باشد.",
    )
    working_hours_weekday = models.CharField(
        "ساعت کاری (شنبه تا چهارشنبه)", max_length=100, blank=True, default="۹:۰۰ الی ۱۸:۰۰"
    )
    working_hours_weekend = models.CharField(
        "ساعت کاری (پنجشنبه‌ها)", max_length=100, blank=True, default="۹:۰۰ الی ۱۳:۰۰"
    )

    meta_title = models.CharField("عنوان SEO سایت", max_length=70, blank=True)
    meta_description = models.CharField("توضیحات متا (SEO)", max_length=160, blank=True)

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return "تنظیمات سایت گارنت"


class MenuItem(models.Model):
    """آیتم‌های منوی اصلی سایت (هدر دسکتاپ و منوی موبایل)؛ از پنل ادمین قابل ویرایش، حذف و مرتب‌سازی است."""

    title = models.CharField("عنوان", max_length=60)
    title_en = models.CharField("عنوان (EN)", max_length=60, blank=True)
    url = models.CharField(
        "لینک", max_length=200, blank=True, default="",
        help_text="مثال: /projects/ یا /#about یا #contact (رفتن به فوتر). برای باز شدن فرم مشاوره، گزینه‌ی پایین را تیک بزنید.",
    )
    open_consult = models.BooleanField(
        "باز کردن فرم مشاوره به‌جای رفتن به لینک", default=False,
    )
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)
    is_active = models.BooleanField("نمایش در منو", default=True)

    class Meta:
        verbose_name = "آیتم منو"
        verbose_name_plural = "آیتم‌های منوی اصلی"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class SiteTheme(SingletonModel):
    """پوسته بصری سایت؛ رنگ، شفافیت و وزن‌های اصلی تایپوگرافی را کنترل می‌کند."""
    background = models.CharField("پس‌زمینه اصلی", max_length=30, default="#F9F9F9")
    surface = models.CharField("سطح / کارت", max_length=30, default="#FFFFFF")
    primary = models.CharField("سرمه‌ای اصلی", max_length=30, default="#092634")
    secondary = models.CharField("آبی اصلی", max_length=30, default="#004E72")
    accent = models.CharField("نارنجی تأکیدی", max_length=30, default="#FF6E42")
    accent_hover = models.CharField("نارنجی حالت Hover", max_length=30, default="#FF9A7D")
    text = models.CharField("رنگ متن اصلی", max_length=30, default="#1A1C1C")
    muted = models.CharField("رنگ متن فرعی", max_length=30, default="#60727D")
    white = models.CharField("سفید", max_length=30, default="#FFFFFF")
    dark = models.CharField("پس‌زمینه تیره", max_length=30, default="#04141E")
    border = models.CharField("رنگ مرز", max_length=30, default="#DCE5E8")
    glass = models.CharField("رنگ شیشه‌ای روشن", max_length=40, default="rgba(255,255,255,.72)")
    glass_dark = models.CharField("رنگ شیشه‌ای تیره", max_length=40, default="rgba(7,29,43,.52)")
    overlay = models.CharField("لایه روی تصاویر", max_length=40, default="rgba(7,29,43,.66)")
    shadow = models.CharField("سایه", max_length=120, default="0 24px 80px rgba(3,18,27,.20)")
    radius = models.PositiveIntegerField("گردی گوشه‌ها (px)", default=22)
    glass_blur = models.PositiveIntegerField("میزان Blur شیشه (px)", default=22)
    body_weight = models.PositiveIntegerField("وزن متن عادی", default=400)
    heading_weight = models.PositiveIntegerField("وزن تیترهای عمومی", default=500)
    hero_weight = models.PositiveIntegerField("وزن تیتر Hero", default=500)
    section_weight = models.PositiveIntegerField("وزن تیتر بخش‌ها", default=500)
    card_weight = models.PositiveIntegerField("وزن تیتر کارت‌ها", default=600)
    nav_weight = models.PositiveIntegerField("وزن منو", default=600)
    button_weight = models.PositiveIntegerField("وزن دکمه‌ها", default=700)
    label_weight = models.PositiveIntegerField("وزن برچسب‌ها", default=600)
    small_weight = models.PositiveIntegerField("وزن متن‌های ریز", default=400)
    # کنترل‌های پیشرفته رابط کاربری
    header_background = models.CharField("پس‌زمینه هدر", max_length=60, default="rgba(255,255,255,.82)")
    header_opacity = models.DecimalField("شفافیت هدر", max_digits=3, decimal_places=2, default=0.82)
    header_blur = models.PositiveIntegerField("Blur هدر (px)", default=22)
    header_border = models.CharField("مرز هدر", max_length=60, default="rgba(9,38,52,.10)")
    header_text = models.CharField("متن هدر", max_length=30, default="#092634")
    header_muted = models.CharField("متن فرعی هدر", max_length=30, default="#60727D")
    header_cta_background = models.CharField("پس‌زمینه دکمه مشاوره هدر", max_length=60, default="rgba(255,255,255,.62)")
    header_cta_text = models.CharField("متن دکمه مشاوره هدر", max_length=30, default="#092634")
    header_cta_border = models.CharField("مرز دکمه مشاوره هدر", max_length=60, default="rgba(9,38,52,.12)")
    menu_line_color = models.CharField("رنگ خطوط منوی موبایل", max_length=30, default="#092634")
    primary_button_background = models.CharField("پس‌زمینه دکمه اصلی", max_length=30, default="#FF6E42")
    primary_button_text = models.CharField("متن دکمه اصلی", max_length=30, default="#081923")
    primary_button_hover = models.CharField("Hover دکمه اصلی", max_length=30, default="#FF9A7D")
    glass_button_background = models.CharField("پس‌زمینه دکمه شیشه‌ای", max_length=60, default="rgba(255,255,255,.10)")
    glass_button_border = models.CharField("مرز دکمه شیشه‌ای", max_length=60, default="rgba(255,255,255,.28)")
    modal_background = models.CharField("پس‌زمینه پاپ‌آپ فرم", max_length=60, default="rgba(248,249,248,.66)")
    modal_border = models.CharField("مرز پاپ‌آپ فرم", max_length=60, default="rgba(255,255,255,.92)")
    footer_background = models.CharField("پس‌زمینه فوتر", max_length=60, default="#04141E")
    footer_text = models.CharField("متن فوتر", max_length=30, default="#FFFFFF")
    hero_overlay = models.CharField("Overlay تصویر Hero (غیرفعال — تصویر/ویدیو بدون کاور نمایش داده می‌شود)", max_length=100, default="transparent")
    logo_width_desktop = models.PositiveIntegerField("ارتفاع لوگو دسکتاپ (px)", default=56, help_text="لوگوی ترکیبی (نماد + نام شرکت) با این ارتفاع و به نسبت اصلی خودش نمایش داده می‌شود.")
    logo_width_mobile = models.PositiveIntegerField("ارتفاع لوگو موبایل (px)", default=46, help_text="لوگوی ترکیبی (نماد + نام شرکت) با این ارتفاع و به نسبت اصلی خودش نمایش داده می‌شود.")
    custom_css = models.TextField("CSS پیشرفته (اختیاری)", blank=True, help_text="برای سفارشی‌سازی حرفه‌ای. فقط CSS معتبر وارد کنید.")

    class Meta:
        verbose_name = "پوسته و طراحی سایت"
        verbose_name_plural = "پوسته و طراحی سایت"

    def __str__(self):
        return "پوسته بصری گارنت"


class HeroSection(SingletonModel):
    """محتوای بخش Hero (اولین بخش صفحه اصلی)."""

    badge_text_en = models.CharField("Hero badge (EN)", max_length=200, blank=True)
    badge_text = models.CharField(
        "متن نشان بالای عنوان", max_length=200, blank=True,
        default="طراحی و ساخت تخصصی ابنیه مدرن | شرکت بهمن ساختار آوید",
    )
    title = models.CharField(
        "عنوان اصلی", max_length=200, default="گارنت؛ آفرینش آپارتمان‌های فاخر و معماری اصیل معاصر"
    )
    title_en = models.CharField("عنوان اصلی (EN)", max_length=200, blank=True)
    subtitle_en = models.TextField("زیرعنوان / توضیح کوتاه (EN)", blank=True)
    subtitle = models.TextField(
        "زیرعنوان / توضیح کوتاه", blank=True,
        default="همنشینی هارمونیک نور، فضا و متریال ناب در ساختمان‌ها و واحدهای مسکونی مدرن. برند «گارنت» با تمرکز انحصاری بر احداث پروژه‌های لوکس و با پشتوانه رسمی شرکت ثبتی «بهمن ساختار آوید»، سازه‌هایی ماندگار و با اصالت مهندسی خلق می‌کند.",
    )
    background_image = models.ImageField(
        "تصویر پس‌زمینه", upload_to="hero/", validators=IMAGE_VALIDATORS, blank=True
    )
    background_video = models.FileField(
        "ویدیوی پس‌زمینه (اختیاری)", upload_to="hero/videos/", validators=VIDEO_VALIDATORS, blank=True,
        help_text="MP4/WebM ترجیحاً 1920×1080، حجم پیشنهادی حداکثر 15MB.",
    )
    primary_button_text_en = models.CharField("متن دکمه اول (EN)", max_length=50, blank=True)
    primary_button_text = models.CharField("متن دکمه اول (نارنجی)", max_length=50, default="پروژه‌های در حال اجرا")
    primary_button_url = models.CharField("لینک دکمه اول", max_length=200, default="#ongoing-projects")
    secondary_button_text_en = models.CharField("متن دکمه دوم (EN)", max_length=50, blank=True)
    secondary_button_text = models.CharField("متن دکمه دوم", max_length=50, default="نمونه‌کارهای اجرا شده")
    secondary_button_url = models.CharField("لینک دکمه دوم", max_length=200, default="#showcase")
    tertiary_button_text_en = models.CharField("متن دکمه سوم (EN)", max_length=50, blank=True)
    tertiary_button_text = models.CharField("متن دکمه سوم (خطی)", max_length=50, blank=True, default="تماس و مشاوره")
    tertiary_button_url = models.CharField("لینک دکمه سوم", max_length=200, blank=True, default="#contact")

    class Meta:
        verbose_name = "بخش Hero"
        verbose_name_plural = "بخش Hero"

    def __str__(self):
        return "محتوای بخش Hero"


class HeroStat(models.Model):
    """آمارهای کوتاه زیر بخش Hero (مثل «۱۰۰٪ نظارت عالیه مهندسی»)."""

    hero = models.ForeignKey(HeroSection, related_name="stats", on_delete=models.CASCADE, verbose_name="بخش Hero")
    value = models.CharField("مقدار / عنوان کوتاه", max_length=50, help_text="مثال: ۱۰۰٪ یا درجه‌یک")
    label_en = models.CharField("توضیح کوتاه (EN)", max_length=150, blank=True)
    label = models.CharField("توضیح کوتاه", max_length=150, help_text="مثال: نظارت عالیه مهندسی")
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "آمار Hero"
        verbose_name_plural = "آمارهای بخش Hero"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.value} — {self.label}"


class Project(models.Model):
    """پروژه‌های انجام‌شده یا در حال اجرای شرکت."""

    STATUS_COMPLETED = "completed"
    STATUS_ONGOING = "ongoing"
    STATUS_CHOICES = [
        (STATUS_COMPLETED, "انجام‌شده"),
        (STATUS_ONGOING, "در حال اجرا"),
    ]

    title = models.CharField("عنوان پروژه", max_length=150)
    title_en = models.CharField("عنوان پروژه (EN)", max_length=150, blank=True)
    code = models.CharField(
        "کد پروژه", max_length=20, blank=True, help_text="مثال: G-26"
    )
    slug = models.SlugField("اسلاگ (URL)", max_length=170, unique=True, allow_unicode=True)
    status = models.CharField("وضعیت پروژه", max_length=20, choices=STATUS_CHOICES)
    status_note_en = models.CharField("توضیح وضعیت اجرایی (EN)", max_length=200, blank=True)
    status_note = models.CharField(
        "توضیح وضعیت اجرایی", max_length=200, blank=True,
        help_text="مثال: تکمیل اسکلت و اجرای تاسیسات",
    )
    location_en = models.CharField("موقعیت مکانی (EN)", max_length=200, blank=True)
    location = models.CharField("موقعیت مکانی", max_length=200, blank=True)
    year = models.PositiveIntegerField("سال", blank=True, null=True)
    short_description = models.CharField("توضیح کوتاه", max_length=300, blank=True)
    short_description_en = models.CharField("توضیح کوتاه (EN)", max_length=300, blank=True)
    full_description = models.TextField("متن کامل معرفی پروژه", blank=True)
    full_description_en = models.TextField("متن کامل معرفی پروژه (EN)", blank=True)
    feature_list_en = models.TextField("اطلاعات پروژه (EN)", blank=True)
    feature_list = models.TextField(
        "اطلاعات پروژه", blank=True,
        help_text="هر اطلاعات یا پاراگراف را در یک خط جداگانه بنویسید؛ کنار هر مورد یک خط مشکی مینیمال برای جداسازی نمایش داده می‌شود.",
    )
    main_image = models.ImageField(
        "تصویر اصلی", upload_to="projects/main/", validators=IMAGE_VALIDATORS, blank=True
    )
    badge_text_en = models.CharField("متن نشان ویژه (EN)", max_length=150, blank=True)
    badge_text = models.CharField(
        "متن نشان ویژه", max_length=150, blank=True,
        help_text="مثال: بزرگ‌ترین پروژه ساختمانی مجموعه گارنت",
    )
    cta_text_en = models.CharField("متن دکمه اقدام (EN)", max_length=50, blank=True)
    cta_text = models.CharField("متن دکمه اقدام", max_length=50, blank=True, default="اطلاعات و پیش‌خرید")
    is_featured = models.BooleanField(
        "نمایش برجسته (مثلاً گارنت میدو)", default=False,
        help_text="برای معرفی برجسته‌تر یک پروژه (مثل پروژه گارنت میدو) فعال کنید.",
    )
    is_active = models.BooleanField("نمایش در سایت", default=True)
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "پروژه"
        verbose_name_plural = "پروژه‌ها"
        ordering = ["-is_featured", "order", "-year"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse("website:project_detail", kwargs={"slug": self.slug})

    @property
    def cover_image(self):
        """تصویر نمایش در کارت‌ها: تصویر اصلی، یا نخستین تصویر گالری اگر تصویر اصلی نباشد."""
        if self.main_image:
            return self.main_image
        first = next(iter(self.images.all()), None)
        return first.image if first else None

    @property
    def features(self):
        return [line.strip() for line in self.feature_list.splitlines() if line.strip()]

    @property
    def features_en(self):
        source = self.feature_list_en or self.feature_list
        return [line.strip() for line in source.splitlines() if line.strip()]

    @property
    def image_category_counts(self):
        """
        تعداد تصاویر گالری این پروژه به تفکیک دسته‌بندی؛ برای نمایش شمارنده
        روی دکمه‌های فیلتر گالری نمونه‌کارها استفاده می‌شود.
        """
        counts = {"exterior": 0, "lobby": 0, "interior": 0, "other": 0}
        images = list(self.images.all())
        for img in images:
            counts[img.category] = counts.get(img.category, 0) + 1
        counts["all"] = len(images)
        return counts


class ProjectImage(models.Model):
    """تصاویر گالری هر پروژه (چندین تصویر با امکان تعیین ترتیب و دسته‌بندی)."""

    CATEGORY_EXTERIOR = "exterior"
    CATEGORY_LOBBY = "lobby"
    CATEGORY_INTERIOR = "interior"
    CATEGORY_OTHER = "other"
    CATEGORY_CHOICES = [
        (CATEGORY_EXTERIOR, "نمای بیرونی"),
        (CATEGORY_LOBBY, "مشاعات و لابی"),
        (CATEGORY_INTERIOR, "فضای داخلی واحدها"),
        (CATEGORY_OTHER, "سایر"),
    ]

    project = models.ForeignKey(Project, related_name="images", on_delete=models.CASCADE, verbose_name="پروژه")
    image = models.ImageField("تصویر", upload_to="projects/gallery/", validators=IMAGE_VALIDATORS)
    caption = models.CharField("عنوان تصویر", max_length=200, blank=True)
    caption_en = models.CharField("عنوان تصویر (EN)", max_length=200, blank=True)
    description = models.CharField("توضیح کوتاه تصویر", max_length=250, blank=True)
    description_en = models.CharField("توضیح کوتاه تصویر (EN)", max_length=250, blank=True)
    category = models.CharField(
        "دسته‌بندی", max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER
    )
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "تصویر پروژه"
        verbose_name_plural = "تصاویر پروژه"
        ordering = ["order", "id"]

    def __str__(self):
        return f"تصویر {self.order} - {self.project.title}"


class PhilosophyFeature(models.Model):
    """ویژگی‌های بخش «فلسفه طراحی و اصالت ساخت» (کارت‌های سه‌گانه)."""

    icon_glyph = models.CharField("آیکون متنی (اموجی یا نویسه)", max_length=10, blank=True, default="✦")
    title = models.CharField("عنوان", max_length=150)
    title_en = models.CharField("عنوان (EN)", max_length=150, blank=True)
    description = models.TextField("توضیح", max_length=400)
    description_en = models.TextField("توضیح (EN)", max_length=400, blank=True)
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)
    is_active = models.BooleanField("نمایش در سایت", default=True)

    class Meta:
        verbose_name = "ویژگی فلسفه ساخت"
        verbose_name_plural = "ویژگی‌های فلسفه ساخت"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class SiteSection(models.Model):
    """
    بخش‌های متنی/محتوایی قابل مدیریت سایت (About، فلسفه طراحی، CTA و ...).
    به‌جای Page Builder پیچیده، هر بخش یک رکورد ساده با کلید مشخص است.
    """

    KEY_ABOUT = "about"
    KEY_WHY_GARNET = "why_garnet"
    KEY_CTA = "cta"
    KEY_CHOICES = [
        (KEY_ABOUT, "معرفی شرکت (About)"),
        (KEY_WHY_GARNET, "فلسفه طراحی و اصالت ساخت"),
        (KEY_CTA, "دعوت به اقدام (CTA)"),
    ]

    key = models.CharField("کلید بخش", max_length=30, choices=KEY_CHOICES, unique=True)
    title = models.CharField("عنوان بخش", max_length=150)
    title_en = models.CharField("عنوان بخش (EN)", max_length=150, blank=True)
    subtitle = models.CharField("زیرعنوان", max_length=250, blank=True)
    subtitle_en = models.CharField("زیرعنوان (EN)", max_length=250, blank=True)
    content = models.TextField("متن بخش")
    content_en = models.TextField("متن بخش (EN)", blank=True)
    quote_text = models.TextField("متن نقل‌قول (اختیاری)", blank=True)
    quote_text_en = models.TextField("متن نقل‌قول (EN)", blank=True)
    quote_author = models.CharField("امضای نقل‌قول", max_length=150, blank=True)
    quote_author_en = models.CharField("امضای نقل‌قول (EN)", max_length=150, blank=True)
    image = models.ImageField(
        "تصویر بخش", upload_to="sections/", validators=IMAGE_VALIDATORS, blank=True
    )
    is_active = models.BooleanField("نمایش در سایت", default=True)
    order = models.PositiveIntegerField("ترتیب نمایش در صفحه", default=0)

    class Meta:
        verbose_name = "بخش سایت"
        verbose_name_plural = "بخش‌های سایت"
        ordering = ["order", "id"]

    def __str__(self):
        return self.get_key_display()


class ConsultationRequest(models.Model):
    """درخواست مشاوره ثبت‌شده توسط کاربران سایت (Lead)."""

    STATUS_NEW = "new"
    STATUS_FOLLOWING = "following"
    STATUS_CALLED = "called"
    STATUS_CONVERTED = "converted"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_NEW, "جدید"),
        (STATUS_FOLLOWING, "در حال پیگیری"),
        (STATUS_CALLED, "تماس گرفته شد"),
        (STATUS_CONVERTED, "تبدیل شد"),
        (STATUS_CLOSED, "بسته شد"),
    ]

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_OTHER = "other"
    GENDER_CHOICES = [(GENDER_MALE, "آقا"), (GENDER_FEMALE, "خانم"), (GENDER_OTHER, "سایر / ترجیح می‌دهم نگویم")]

    name = models.CharField("نام و نام‌خانوادگی", max_length=100)
    gender = models.CharField("عنوان", max_length=10, choices=GENDER_CHOICES, default=GENDER_MALE)
    phone = models.CharField("شماره تماس", max_length=20, validators=[phone_validator])
    subject = models.CharField("موضوع درخواست", max_length=150, blank=True)
    message = models.TextField("توضیح کوتاه", max_length=1000, blank=True)
    status = models.CharField("وضعیت پیگیری", max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    ip_address = models.GenericIPAddressField("آدرس IP", blank=True, null=True)

    class Meta:
        verbose_name = "درخواست مشاوره"
        verbose_name_plural = "درخواست‌های مشاوره"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"


class CompanyCatalog(models.Model):
    """کاتالوگ شرکت؛ فایل از پنل مدیریت قابل جایگزینی است."""
    title = models.CharField("عنوان کاتالوگ", max_length=150, default="کاتالوگ شرکت")
    title_en = models.CharField("عنوان کاتالوگ (EN)", max_length=150, default="Company Catalog", blank=True)
    file = models.FileField("فایل کاتالوگ", upload_to="catalogs/", validators=PDF_VALIDATORS)
    is_active = models.BooleanField("فعال", default=True)
    updated_at = models.DateTimeField("آخرین بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "کاتالوگ شرکت"
        verbose_name_plural = "کاتالوگ شرکت"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    """مقالات دوزبانه برای SEO و محتوای تخصصی برند."""
    title = models.CharField("عنوان", max_length=220)
    title_en = models.CharField("عنوان (EN)", max_length=220, blank=True)
    slug = models.SlugField("Slug", max_length=240, unique=True)
    excerpt = models.TextField("خلاصه", max_length=500, blank=True)
    excerpt_en = models.TextField("خلاصه (EN)", max_length=500, blank=True)
    content = models.TextField("متن مقاله")
    content_en = models.TextField("متن مقاله (EN)", blank=True)
    cover = models.ImageField("تصویر کاور", upload_to="blog/", validators=IMAGE_VALIDATORS, blank=True)
    seo_title = models.CharField("عنوان SEO", max_length=70, blank=True)
    seo_title_en = models.CharField("عنوان SEO (EN)", max_length=70, blank=True)
    seo_description = models.CharField("توضیحات SEO", max_length=160, blank=True)
    seo_description_en = models.CharField("توضیحات SEO (EN)", max_length=160, blank=True)
    category = models.CharField("دسته‌بندی", max_length=100, default="معماری")
    category_en = models.CharField("دسته‌بندی (EN)", max_length=100, default="Architecture", blank=True)
    is_published = models.BooleanField("منتشر شود", default=False)
    is_featured = models.BooleanField("مقاله ویژه", default=False)
    published_at = models.DateTimeField("تاریخ و زمان انتشار", blank=True, null=True, help_text="اگر خالی بماند، هنگام انتشار مقاله، زمان همان لحظه ثبت می‌شود.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مقاله وبلاگ"
        verbose_name_plural = "مقالات وبلاگ"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("website:blog_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        # با منتشر شدن مقاله، زمان انتشار به‌صورت خودکار ثبت می‌شود.
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def display_date(self):
        """زمان نمایشی مقاله: تاریخ انتشار، و در نبود آن تاریخ ثبت."""
        return self.published_at or self.created_at


SITE_TEXT_DEFAULTS = {
    "all_articles_link": ("همه مقالات", "All articles"),
    "all_projects_btn": ("مشاهده همه پروژه‌ها", "View all projects"),
    "journal_eyebrow": ("بلاگ گارنت", "GARNET JOURNAL"),
    "journal_title": ("ایده‌هایی پشت معماری.", "Ideas behind the architecture."),
    "blog_page_eyebrow": ("بلاگ گارنت", "GARNET JOURNAL"),
    "blog_page_title": ("معماری، متریال و ایده‌ها.", "Architecture, materials and ideas."),
    "cta_eyebrow": ("مشاوره خصوصی", "PRIVATE CONSULTATION"),
    "cta_text": ("برای آدرس بعدی شما، یک گفت‌وگوی دقیق و خصوصی.", "A focused conversation for your next address."),
    "cta_button": ("درخواست مشاوره", "Request consultation"),
    "consultation_button_text": ("درخواست مشاوره", "Request consultation"),
    "modal_eyebrow": ("مشاوره خصوصی", "PRIVATE CONSULTATION"),
    "modal_title": ("آدرس بعدی را با هم بسازیم.", "Let's shape the next address."),
    "modal_subtitle": ("برای شروع، چند اطلاعات کوتاه و خصوصی کافی است.", "A short, private brief is enough to start."),
    "submit_text": ("ثبت درخواست", "Send request"),
    "label_name": ("نام و نام‌خانوادگی", "Full name"),
    "label_gender": ("عنوان", "Title"),
    "label_phone": ("شماره تماس همراه", "Phone number"),
    "label_subject": ("موضوع درخواست", "Project subject"),
    "label_message": ("توضیحات یا خلاصه پروژه (اختیاری)", "Project notes (optional)"),
    "ph_name": ("مثال: مهندس رادمنش", "Your full name"),
    "ph_phone": ("۰۹۱۲XXXXXXX", "+98 / 09…"),
    "ph_subject": ("موضوع درخواست", "Project subject"),
    "ph_message": ("نوع پروژه، منطقه، متراژ یا سوال مورد نظر...", "Project type, location, area or question…"),
    "opt_male": ("آقا", "Mr."),
    "opt_female": ("خانم", "Ms."),
    "opt_other": ("سایر / ترجیح می‌دهم نگویم", "Prefer not to say"),
}


class NewsletterSubscriber(models.Model):
    """Email subscriptions collected from the footer newsletter form."""
    email = models.EmailField("ایمیل", unique=True, max_length=254)
    is_active = models.BooleanField("عضویت فعال", default=True)
    created_at = models.DateTimeField("تاریخ عضویت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین به‌روزرسانی", auto_now=True)

    class Meta:
        verbose_name = "عضو خبرنامه"
        verbose_name_plural = "اعضای خبرنامه"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class SiteTexts(SingletonModel):
    """متن‌های قابل ویرایش عنوان‌ها، کادر مشاوره و فرم درخواست؛ هر متن در فارسی و انگلیسی.
    اگر فیلدی خالی بماند، متن پیش‌فرض سایت نمایش داده می‌شود."""

    all_articles_link = models.CharField("لینک «همه مقالات»", max_length=250, blank=True, default="همه مقالات")
    all_articles_link_en = models.CharField("لینک «همه مقالات» (EN)", max_length=250, blank=True, default="All articles")
    all_projects_btn = models.CharField("متن دکمه «مشاهده همه پروژه‌ها»", max_length=250, blank=True, default="مشاهده همه پروژه‌ها")
    all_projects_btn_en = models.CharField("متن دکمه «مشاهده همه پروژه‌ها» (EN)", max_length=250, blank=True, default="View all projects")
    journal_eyebrow = models.CharField("برچسب کوچک کارت بلاگ", max_length=250, blank=True, default="بلاگ گارنت")
    journal_eyebrow_en = models.CharField("برچسب کوچک کارت بلاگ (EN)", max_length=250, blank=True, default="GARNET JOURNAL")
    journal_title = models.CharField("تیتر کارت بلاگ", max_length=250, blank=True, default="ایده‌هایی پشت معماری.")
    journal_title_en = models.CharField("تیتر کارت بلاگ (EN)", max_length=250, blank=True, default="Ideas behind the architecture.")
    blog_page_eyebrow = models.CharField("برچسب کوچک بالای تیتر صفحه مقالات", max_length=250, blank=True, default="بلاگ گارنت")
    blog_page_eyebrow_en = models.CharField("برچسب کوچک بالای تیتر صفحه مقالات (EN)", max_length=250, blank=True, default="GARNET JOURNAL")
    blog_page_title = models.CharField("تیتر صفحه مقالات", max_length=250, blank=True, default="معماری، متریال و ایده‌ها.")
    blog_page_title_en = models.CharField("تیتر صفحه مقالات (EN)", max_length=250, blank=True, default="Architecture, materials and ideas.")
    cta_eyebrow = models.CharField("برچسب کوچک کادر مشاوره", max_length=250, blank=True, default="مشاوره خصوصی")
    cta_eyebrow_en = models.CharField("برچسب کوچک کادر مشاوره (EN)", max_length=250, blank=True, default="PRIVATE CONSULTATION")
    cta_text = models.CharField("متن کادر مشاوره", max_length=250, blank=True, default="برای آدرس بعدی شما، یک گفت‌وگوی دقیق و خصوصی.")
    cta_text_en = models.CharField("متن کادر مشاوره (EN)", max_length=250, blank=True, default="A focused conversation for your next address.")
    cta_button = models.CharField("متن دکمه کادر مشاوره", max_length=250, blank=True, default="درخواست مشاوره")
    consultation_button_text = models.CharField("متن دکمه درخواست مشاوره در سراسر سایت", max_length=120, blank=True, default="درخواست مشاوره")
    consultation_button_text_en = models.CharField("متن دکمه درخواست مشاوره در سراسر سایت (EN)", max_length=120, blank=True, default="Request consultation")
    cta_button_en = models.CharField("متن دکمه کادر مشاوره (EN)", max_length=250, blank=True, default="Request consultation")
    modal_eyebrow = models.CharField("برچسب کوچک بالای فرم", max_length=250, blank=True, default="مشاوره خصوصی")
    modal_eyebrow_en = models.CharField("برچسب کوچک بالای فرم (EN)", max_length=250, blank=True, default="PRIVATE CONSULTATION")
    modal_title = models.CharField("تیتر فرم", max_length=250, blank=True, default="آدرس بعدی را با هم بسازیم.")
    modal_title_en = models.CharField("تیتر فرم (EN)", max_length=250, blank=True, default="Let's shape the next address.")
    modal_subtitle = models.CharField("توضیح زیر تیتر فرم", max_length=250, blank=True, default="برای شروع، چند اطلاعات کوتاه و خصوصی کافی است.")
    modal_subtitle_en = models.CharField("توضیح زیر تیتر فرم (EN)", max_length=250, blank=True, default="A short, private brief is enough to start.")
    submit_text = models.CharField("متن دکمه ارسال فرم", max_length=250, blank=True, default="ثبت درخواست")
    submit_text_en = models.CharField("متن دکمه ارسال فرم (EN)", max_length=250, blank=True, default="Send request")
    label_name = models.CharField("عنوان فیلد نام", max_length=250, blank=True, default="نام و نام‌خانوادگی")
    label_name_en = models.CharField("عنوان فیلد نام (EN)", max_length=250, blank=True, default="Full name")
    label_gender = models.CharField("عنوان فیلد «عنوان»", max_length=250, blank=True, default="عنوان")
    label_gender_en = models.CharField("عنوان فیلد «عنوان» (EN)", max_length=250, blank=True, default="Title")
    label_phone = models.CharField("عنوان فیلد شماره تماس", max_length=250, blank=True, default="شماره تماس همراه")
    label_phone_en = models.CharField("عنوان فیلد شماره تماس (EN)", max_length=250, blank=True, default="Phone number")
    label_subject = models.CharField("عنوان فیلد موضوع", max_length=250, blank=True, default="موضوع درخواست")
    label_subject_en = models.CharField("عنوان فیلد موضوع (EN)", max_length=250, blank=True, default="Project subject")
    label_message = models.CharField("عنوان فیلد توضیحات", max_length=250, blank=True, default="توضیحات یا خلاصه پروژه (اختیاری)")
    label_message_en = models.CharField("عنوان فیلد توضیحات (EN)", max_length=250, blank=True, default="Project notes (optional)")
    ph_name = models.CharField("راهنمای فیلد نام", max_length=250, blank=True, default="مثال: مهندس رادمنش")
    ph_name_en = models.CharField("راهنمای فیلد نام (EN)", max_length=250, blank=True, default="Your full name")
    ph_phone = models.CharField("راهنمای فیلد شماره تماس", max_length=250, blank=True, default="۰۹۱۲XXXXXXX")
    ph_phone_en = models.CharField("راهنمای فیلد شماره تماس (EN)", max_length=250, blank=True, default="+98 / 09…")
    ph_subject = models.CharField("راهنمای فیلد موضوع", max_length=250, blank=True, default="موضوع درخواست")
    ph_subject_en = models.CharField("راهنمای فیلد موضوع (EN)", max_length=250, blank=True, default="Project subject")
    ph_message = models.CharField("راهنمای فیلد توضیحات", max_length=250, blank=True, default="نوع پروژه، منطقه، متراژ یا سوال مورد نظر...")
    ph_message_en = models.CharField("راهنمای فیلد توضیحات (EN)", max_length=250, blank=True, default="Project type, location, area or question…")
    opt_male = models.CharField("گزینه اول", max_length=250, blank=True, default="آقا")
    opt_male_en = models.CharField("گزینه اول (EN)", max_length=250, blank=True, default="Mr.")
    opt_female = models.CharField("گزینه دوم", max_length=250, blank=True, default="خانم")
    opt_female_en = models.CharField("گزینه دوم (EN)", max_length=250, blank=True, default="Ms.")
    opt_other = models.CharField("گزینه سوم", max_length=250, blank=True, default="سایر / ترجیح می‌دهم نگویم")
    opt_other_en = models.CharField("گزینه سوم (EN)", max_length=250, blank=True, default="Prefer not to say")

    class Meta:
        verbose_name = "متن‌های عنوان‌ها و فرم"
        verbose_name_plural = "متن‌های عنوان‌ها و فرم"

    def __str__(self):
        return "متن‌های عنوان‌ها و فرم"

    def resolve(self, lang="fa"):
        """متن‌های نهایی را برای زبان داده‌شده برمی‌گرداند (خالی = پیش‌فرض)."""
        out = {}
        for key, (fa, en) in SITE_TEXT_DEFAULTS.items():
            if lang == "en":
                out[key] = (getattr(self, key + "_en") or "").strip() or en
            else:
                out[key] = (getattr(self, key) or "").strip() or fa
        return out
