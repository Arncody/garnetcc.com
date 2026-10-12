from django.db import migrations, models

LOGO_HELP = "لوگوی ترکیبی (نماد + نام شرکت) با این ارتفاع و به نسبت اصلی خودش نمایش داده می‌شود."


def bigger_logo_defaults(apps, schema_editor):
    """لوگوی ترکیبی (نماد + نام) به ارتفاع بیشتری نیاز دارد؛ فقط مقدارهای پیش‌فرض قدیمی تغییر می‌کنند."""
    SiteTheme = apps.get_model("website", "SiteTheme")
    SiteTheme.objects.filter(logo_width_desktop=48).update(logo_width_desktop=56)
    SiteTheme.objects.filter(logo_width_mobile=42).update(logo_width_mobile=46)


class Migration(migrations.Migration):
    dependencies = [("website", "0006_sitetexts")]
    operations = [
        migrations.AlterField(
            model_name="sitesettings", name="logo",
            field=models.ImageField(blank=True, help_text="لوگوی کامل شرکت را آپلود کنید؛ به‌تنهایی (بدون متن جداگانه) در هدر و فوتر نمایش داده می‌شود. در نبود لوگو، نام برند نوشته می‌شود.", upload_to="site/", verbose_name="لوگو (ترکیبی: نماد + نام شرکت)"),
        ),
        migrations.AlterField(
            model_name="sitetheme", name="logo_width_desktop",
            field=models.PositiveIntegerField(default=56, help_text=LOGO_HELP, verbose_name="ارتفاع لوگو دسکتاپ (px)"),
        ),
        migrations.AlterField(
            model_name="sitetheme", name="logo_width_mobile",
            field=models.PositiveIntegerField(default=46, help_text=LOGO_HELP, verbose_name="ارتفاع لوگو موبایل (px)"),
        ),
        migrations.AlterField(
            model_name="project", name="feature_list",
            field=models.TextField(blank=True, help_text="هر اطلاعات یا پاراگراف را در یک خط جداگانه بنویسید؛ کنار هر مورد یک خط مشکی مینیمال برای جداسازی نمایش داده می‌شود.", verbose_name="اطلاعات پروژه"),
        ),
        migrations.AlterField(
            model_name="project", name="feature_list_en",
            field=models.TextField(blank=True, verbose_name="اطلاعات پروژه (EN)"),
        ),
        migrations.RunPython(bigger_logo_defaults, migrations.RunPython.noop),
    ]
