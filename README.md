# Garnet — Luxury Glass UI Django

این نسخه فرانت Stitch را به ساختار Django متصل کرده و برای دسکتاپ، تبلت و موبایل responsive است.

## اجرا
1. `python -m venv .venv`
2. فعال‌سازی محیط و `pip install -r requirements.txt`
3. کپی `.env.example` به `.env` و تعیین `SECRET_KEY`
4. `python manage.py migrate`
5. `python manage.py seed_data`
6. `python manage.py createsuperuser`
7. `python manage.py runserver`

## امکانات این نسخه
- UI شیشه‌ای مدرن با زمینه سرمه‌ای عمیق و خوانایی بالا.
- هدر glassmorphism و فوتر استاندارد چهارستونه + bottom bar.
- سه CTA هیرو بدون آیکون و با استایل ساده/لوکس.
- فرم شیشه‌ای با انتخاب «آقا / خانم / سایر».
- فارسی/انگلیسی با ذخیره زبان در session.
- فیلدهای انگلیسی قابل ویرایش برای محتوای اصلی در Django Admin.
- فونت IRANSansWebFaNum به‌صورت Local و یکپارچه در کل سایت (فرانت و پنل ادمین).
- تمام پروژه‌ها، خدمات، تصاویر و لیدهای فرم از بک‌اند Django خوانده می‌شوند.
- صفحات جزئیات پروژه از همان پوسته استفاده می‌کنند.
- محدودیت ضداسپم فرم و honeypot حفظ شده است.

## راهنمای ابعاد تصاویر
- Hero background: `2560×1600` px (نسبت 16:10)، JPG/WebP، سوژه اصلی در مرکز امن.
- Project main: `1600×1100` px (نسبت حدود 3:2)، JPG/WebP.
- Project gallery: `1600×1200` px (4:3) یا `1920×1280` px (3:2).
- Section image: `1400×1100` px، JPG/WebP.
- Service icon: `256×256` px، PNG/WebP با پس‌زمینه شفاف.
- Logo: ترجیحاً SVG؛ در صورت raster حداقل `800×800` px با پس‌زمینه شفاف.

برای کیفیت سریع و حرفه‌ای، WebP/AVIF برای تصاویر وب پیشنهاد می‌شود و تصاویر را قبل از آپلود به ابعاد بالا محدود کنید.


## V9 UI / Admin enhancements
- Mobile header now has unified language and consultation controls.
- Consultation dialog uses a single internal scrollbar; the dialog itself no longer creates a second scrollbar.
- Added `SiteTheme` singleton for centralized visual tokens, glass effects, radius/blur and typography weights.
- Admin panel includes a dedicated «پوسته و طراحی سایت» section with color pickers, glass/shadow controls and typography weights.
- Run `python manage.py migrate` after replacing the project files.
