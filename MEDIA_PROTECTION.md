# محافظت از عکس و ویدیو

عکس‌ها و ویدیوهای آپلود‌شده از مسیر `/media/` و از طریق Django (`website/media_views.py`) سرو می‌شوند و این قواعد اعمال می‌شود:

- فقط وقتی داخل صفحه‌ی همین سایت (`<img>` / `<video>` / background) بارگذاری شوند نمایش داده می‌شوند.
- باز کردن مستقیم لینک فایل در تب جدید، `fetch`/XHR و hotlink از سایت‌های دیگر ← **403**.
- ویدیو: مرورگر مدرن (Chrome/Firefox) روی HTTPS یا localhost که هدرهای `Sec-Fetch-*` نفرستد (مثل درخواست جداگانه‌ی IDM و دانلودرها) ← **403**.
- مدیران سایت (staff) در پنل ادمین همه‌چیز را می‌بینند. پوشه‌ی `site/` (لوگو) عمومی است. فایل‌های غیرتصویری مثل **کاتالوگ PDF** عمداً قابل دانلودند.
- پشتیبانی کامل از Range (برای پخش و جلو/عقب‌کردن ویدیو، به‌ویژه در iOS).

## Production
۱) ساده‌ترین حالت: در Nginx مسیر `/media/` را به Django پروکسی کنید (نه `alias` مستقیم):

```
location /media/ { proxy_pass http://127.0.0.1:8000; proxy_set_header Host $host; proxy_set_header X-Forwarded-Proto $scheme; }
```

۲) حالت پرسرعت (Nginx ارسال فایل را انجام می‌دهد، Django فقط اجازه می‌دهد):

```
location /protected-media/ { internal; alias /path/to/project/media/; }
location /media/ { proxy_pass http://127.0.0.1:8000; proxy_set_header Host $host; proxy_set_header X-Forwarded-Proto $scheme; }
```
و در `.env`: `MEDIA_ACCEL_REDIRECT=/protected-media/`

برای خاموش‌کردن موقت: `PROTECT_MEDIA=False`.

## محدودیت واقعی
هر چیزی که مرورگر نمایش می‌دهد با اسکرین‌شات یا DevTools قابل ذخیره است؛ این سیستم دانلود ساده/خودکار را متوقف می‌کند، نه کپی دستی را.
نوار «دانلود فایل تصویری از این صفحه» مربوط به افزونه‌ی IDM روی کامپیوتر خود شماست و جزو سایت نیست.
