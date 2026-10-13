"""
website/storage.py
ذخیره‌ساز فایل با نام امن (ASCII).

مشکل: روی بعضی هاست‌ها (cPanel/LiteSpeed) زبان سیستم ASCII است و ذخیره‌ی فایلی با
نام فارسی (مثل «فاکتور.pdf») خطای UnicodeEncodeError می‌دهد.
راه‌حل: اگر نام فایل شامل حرف غیر ASCII باشد، با یک نام تصادفی امن جایگزین می‌شود.
نام‌های انگلیسی مثل قبل بدون تغییر می‌مانند.
"""
import os
import re
import uuid

from django.core.files.storage import FileSystemStorage

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


class SafeFileSystemStorage(FileSystemStorage):
    def get_valid_name(self, name):
        base, ext = os.path.splitext(os.path.basename(str(name)))
        ext = _SAFE.sub("", ext.lower())
        if not ext.isascii():
            ext = ""
        clean = _SAFE.sub("_", base).strip("._-")
        if not clean or not base.isascii() or not clean.strip("_"):
            clean = uuid.uuid4().hex[:12]
        return f"{clean[:80]}{ext}"
