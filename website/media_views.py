"""
website/media_views.py
سرو محافظت‌شده‌ی فایل‌های Media (عکس و ویدیو).

هدف: عکس و ویدیوها فقط داخل خودِ صفحات سایت نمایش داده شوند و
  - باز کردن مستقیم لینک فایل در تب جدید،
  - «ذخیره/دانلود» توسط ابزارهای دانلودر (مثل IDM) که درخواست جداگانه می‌فرستند،
  - اسکریپت‌ها/fetch و hotlink از سایت‌های دیگر
بلاک شوند. هر چیزی که مرورگر نمایش می‌دهد را نمی‌شود ۱۰۰٪ از دسترس خارج کرد
(اسکرین‌شات / DevTools)، ولی این لایه‌ها دانلود ساده و خودکار را عملاً از بین می‌برند.
"""
import mimetypes
import os
import re

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotModified, StreamingHttpResponse
from django.utils._os import safe_join
from django.utils.http import http_date, parse_http_date_safe
from django.views.decorators.http import require_http_methods

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
VIDEO_EXT = {".mp4", ".webm", ".mov", ".m4v", ".ogv"}
PUBLIC_PREFIXES = ("site/",)          # لوگو/فاویکون: عمومی (مثلاً برای پیش‌نمایش لینک)
ALLOWED_DEST = {"image", "video"}     # مقصدهایی که مرورگر برای <img> / <video> / background می‌فرستد
CHUNK = 64 * 1024

_MODERN_UA = re.compile(r"(?:Chrome|Chromium|Edg|OPR)/(\d+)|Firefox/(\d+)")


def _expects_fetch_metadata(request):
    """مرورگرهای مدرن (Chrome 80+ / Firefox 90+) روی HTTPS یا localhost همیشه Sec-Fetch-* می‌فرستند."""
    if not (request.is_secure() or request.get_host().split(":")[0] in {"localhost", "127.0.0.1", "[::1]"}):
        return False
    m = _MODERN_UA.search(request.META.get("HTTP_USER_AGENT", ""))
    if not m:
        return False
    return int(m.group(1)) >= 80 if m.group(1) else int(m.group(2)) >= 90


def _same_host(url, request):
    from urllib.parse import urlparse
    try:
        return urlparse(url).netloc.lower() == request.get_host().lower()
    except Exception:
        return False


def _allowed(request, rel_path, ext):
    user = getattr(request, "user", None)
    if user is not None and user.is_staff:
        return True                               # مدیران سایت (پیش‌نمایش در پنل ادمین)
    if rel_path.startswith(PUBLIC_PREFIXES):
        return True
    dest = request.headers.get("Sec-Fetch-Dest")
    site = request.headers.get("Sec-Fetch-Site")
    if dest is not None:
        # درخواست واقعی مرورگر: فقط تصویر/ویدیوی داخل صفحه‌ی همین سایت
        return dest in ALLOWED_DEST and site in {"same-origin", "same-site"}
    # بدون Sec-Fetch-*: مرورگر قدیمی، یا ابزار دانلودر که درخواست جداگانه می‌فرستد
    if ext in VIDEO_EXT and _expects_fetch_metadata(request):
        return False                              # مرورگر مدرن بدون این هدرها = ابزار دانلود
    ref = request.headers.get("Referer") or request.headers.get("Origin")
    if ref:
        return _same_host(ref, request)           # hotlink از سایت دیگر
    return not _expects_fetch_metadata(request) if ext in VIDEO_EXT else True


def _iter_file(path, start, length):
    with open(path, "rb") as fh:
        fh.seek(start)
        remaining = length
        while remaining > 0:
            data = fh.read(min(CHUNK, remaining))
            if not data:
                break
            remaining -= len(data)
            yield data


def _harden(response, ext, public=False):
    response["Content-Disposition"] = "inline"
    response["X-Content-Type-Options"] = "nosniff"
    response["Cross-Origin-Resource-Policy"] = "cross-origin" if public else "same-origin"
    response["Cache-Control"] = "private, max-age=3600"
    response["Vary"] = "Sec-Fetch-Dest, Sec-Fetch-Site, Referer"
    if not public:
        response["X-Robots-Tag"] = "noindex"
    return response


@require_http_methods(["GET", "HEAD"])
def protected_media(request, path):
    try:
        full = safe_join(settings.MEDIA_ROOT, path)
    except Exception:
        raise Http404
    if not os.path.isfile(full):
        raise Http404
    rel = path.replace("\\", "/").lstrip("/")
    ext = os.path.splitext(full)[1].lower()
    public = rel.startswith(PUBLIC_PREFIXES)
    protected = ext in IMAGE_EXT or ext in VIDEO_EXT

    if protected and getattr(settings, "PROTECT_MEDIA", True) and not _allowed(request, rel, ext):
        return HttpResponseForbidden("Forbidden")

    ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"

    if not protected:
        # فایل‌های دیگر (مثل کاتالوگ PDF) عمداً قابل دانلود هستند.
        from django.views.static import serve
        return serve(request, path, document_root=settings.MEDIA_ROOT)

    accel = getattr(settings, "MEDIA_ACCEL_REDIRECT", "")
    if accel:                                     # Nginx خودش Range/ارسال را انجام می‌دهد
        resp = HttpResponse(content_type=ctype)
        resp["X-Accel-Redirect"] = accel.rstrip("/") + "/" + rel
        return _harden(resp, ext, public)

    stat = os.stat(full)
    size = stat.st_size
    mtime = int(stat.st_mtime)
    ims = parse_http_date_safe(request.headers.get("If-Modified-Since", ""))
    if ims is not None and mtime <= ims and "Range" not in request.headers:
        return _harden(HttpResponseNotModified(), ext, public)

    start, end, status = 0, size - 1, 200
    rng = request.headers.get("Range")
    if rng:
        m = re.fullmatch(r"bytes=(\d*)-(\d*)", rng.strip())
        if not m or (m.group(1) == "" and m.group(2) == ""):
            resp = HttpResponse(status=416)
            resp["Content-Range"] = f"bytes */{size}"
            return resp
        if m.group(1) == "":                       # آخرین N بایت
            start = max(size - int(m.group(2)), 0)
        else:
            start = int(m.group(1))
            if m.group(2):
                end = min(int(m.group(2)), size - 1)
        if start >= size or start > end:
            resp = HttpResponse(status=416)
            resp["Content-Range"] = f"bytes */{size}"
            return resp
        status = 206

    length = end - start + 1
    if request.method == "HEAD":
        resp = HttpResponse(status=status, content_type=ctype)
    else:
        resp = StreamingHttpResponse(_iter_file(full, start, length), status=status, content_type=ctype)
    resp["Content-Length"] = str(length)
    resp["Accept-Ranges"] = "bytes"
    resp["Last-Modified"] = http_date(mtime)
    if status == 206:
        resp["Content-Range"] = f"bytes {start}-{end}/{size}"
    return _harden(resp, ext, public)
