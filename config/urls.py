"""
config/urls.py
وظیفه: نگاشت URLهای اصلی پروژه به اپلیکیشن website و پنل ادمین.
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from website.sitemaps import ProjectSitemap, StaticViewSitemap
from website.media_views import protected_media

sitemaps = {
    "projects": ProjectSitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("gnt-8xK29/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", include("website.urls")),
]

# سرو محافظت‌شده‌ی فایل‌های Media (عکس/ویدیو فقط داخل صفحات سایت؛ بدون دانلود مستقیم).
# در Production این مسیر باید به Django برسد (یا از MEDIA_ACCEL_REDIRECT استفاده شود)؛ راهنما: MEDIA_PROTECTION.md
urlpatterns += [
    re_path(r"^%s(?P<path>.*)$" % settings.MEDIA_URL.lstrip("/"), protected_media, name="protected_media"),
]
