"""
config/wsgi.py
وظیفه: نقطه ورود WSGI برای اجرای پروژه روی هاست اشتراکی (مثلاً Phusion Passenger)
یا هر سرور WSGI دیگر مانند gunicorn.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

# برخی هاست‌های اشتراکی (مثل cPanel با Passenger) انتظار متغیر
# 'application' را دارند که در بالا تعریف شده است. اگر هاست شما به‌جای آن
# نیاز به نام دیگری دارد (مثلاً app)، همین شیء را به آن نام هم نگاشت کنید:
# app = application
