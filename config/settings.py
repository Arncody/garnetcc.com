"""
config/settings.py
وظیفه: تنظیمات مرکزی پروژه Django (امنیت، دیتابیس، static/media، اپلیکیشن‌ها).
تمام مقادیر حساس از Environment Variable خوانده می‌شوند تا هیچ اطلاعات حساسی
داخل کد قرار نگیرد (مناسب برای هاست اشتراکی و Production).
"""

from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------
# امنیت پایه
# -----------------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY", default="").strip()
DEBUG = config("DEBUG", default=False, cast=bool)
if not SECRET_KEY or SECRET_KEY.lower().startswith(("change-this", "django-insecure-", "replace-me", "replace_with")):
    if not DEBUG:
        raise RuntimeError("Production requires a strong, unique SECRET_KEY in environment/.env.")
    if not SECRET_KEY:
        raise RuntimeError("Set SECRET_KEY in .env before starting Django.")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())
if not DEBUG and (not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS):
    raise RuntimeError("Set explicit ALLOWED_HOSTS for production.")

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS", default="", cast=Csv()
)

# -----------------------------------------------------------------------
# اپلیکیشن‌ها
# -----------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "website",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # تزریق تنظیمات سایت (SiteSettings) در همه‌ی قالب‌ها
                "website.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# -----------------------------------------------------------------------
# دیتابیس
# در Development به‌طور پیش‌فرض SQLite است. برای Production با تنظیم
# DB_ENGINE=postgres در .env می‌توان به PostgreSQL سوییچ کرد.
# -----------------------------------------------------------------------
if config("DB_ENGINE", default="sqlite") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# -----------------------------------------------------------------------
# اعتبارسنجی رمز عبور (برای کاربران ادمین)
# -----------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------
# زبان، منطقه زمانی و RTL
# -----------------------------------------------------------------------
LANGUAGE_CODE = "fa"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------
# فایل‌های Static و Media
# -----------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# محافظت از عکس/ویدیو در برابر دانلود مستقیم و دانلودرها (جزئیات در MEDIA_PROTECTION.md)
PROTECT_MEDIA = config("PROTECT_MEDIA", default=True, cast=bool)
# اگر Nginx فایل‌ها را سرو می‌کند، مسیر internal آن را اینجا بدهید (مثلاً /protected-media/)
MEDIA_ACCEL_REDIRECT = config("MEDIA_ACCEL_REDIRECT", default="")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------------
# محدودیت‌های آپلود فایل (جلوگیری از آپلود فایل‌های سنگین/مخرب)
# -----------------------------------------------------------------------
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024   # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024   # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644

# -----------------------------------------------------------------------
# Cache (استفاده برای Rate Limiting فرم مشاوره - نیازی به Redis نیست)
# -----------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "garnet-cache",
    }
}

# -----------------------------------------------------------------------
# تنظیمات امنیتی که فقط در Production (DEBUG=False) فعال می‌شوند
# -----------------------------------------------------------------------
# HTTP security headers. Enable redirect only when HTTPS is configured correctly
# at the host/proxy. HSTS subdomains/preload are opt-in to avoid locking out
# unrelated subdomains on shared hosting.
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=not DEBUG, cast=bool)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = config("CSRF_COOKIE_HTTPONLY", default=False, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = config("SECURE_REFERRER_POLICY", default="same-origin")
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0 if DEBUG else 86400, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False, cast=bool)
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=False, cast=bool)
# Only set SECURE_PROXY_SSL_HEADER if the hosting provider confirms its proxy header.
if config("USE_X_FORWARDED_PROTO", default=False, cast=bool):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# نمایش صفحه خطای سفارشی 404/500 در Production (به‌جای Debug Page)
