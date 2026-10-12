from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("website", "0002_compact_luxury")]

    operations = [
        migrations.CreateModel(
            name="SiteTheme",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("background", models.CharField(default="#F9F9F9", max_length=30, verbose_name="پس‌زمینه اصلی")),
                ("surface", models.CharField(default="#FFFFFF", max_length=30, verbose_name="سطح / کارت")),
                ("primary", models.CharField(default="#092634", max_length=30, verbose_name="سرمه‌ای اصلی")),
                ("secondary", models.CharField(default="#004E72", max_length=30, verbose_name="آبی اصلی")),
                ("accent", models.CharField(default="#FF6E42", max_length=30, verbose_name="نارنجی تأکیدی")),
                ("accent_hover", models.CharField(default="#FF9A7D", max_length=30, verbose_name="نارنجی حالت Hover")),
                ("text", models.CharField(default="#1A1C1C", max_length=30, verbose_name="رنگ متن اصلی")),
                ("muted", models.CharField(default="#60727D", max_length=30, verbose_name="رنگ متن فرعی")),
                ("white", models.CharField(default="#FFFFFF", max_length=30, verbose_name="سفید")),
                ("dark", models.CharField(default="#04141E", max_length=30, verbose_name="پس‌زمینه تیره")),
                ("border", models.CharField(default="#DCE5E8", max_length=30, verbose_name="رنگ مرز")),
                ("glass", models.CharField(default="rgba(255,255,255,.72)", max_length=40, verbose_name="رنگ شیشه‌ای روشن")),
                ("glass_dark", models.CharField(default="rgba(7,29,43,.52)", max_length=40, verbose_name="رنگ شیشه‌ای تیره")),
                ("overlay", models.CharField(default="rgba(7,29,43,.66)", max_length=40, verbose_name="لایه روی تصاویر")),
                ("shadow", models.CharField(default="0 24px 80px rgba(3,18,27,.20)", max_length=120, verbose_name="سایه")),
                ("radius", models.PositiveIntegerField(default=22, verbose_name="گردی گوشه‌ها (px)")),
                ("glass_blur", models.PositiveIntegerField(default=22, verbose_name="میزان Blur شیشه (px)")),
                ("body_weight", models.PositiveIntegerField(default=400, verbose_name="وزن متن عادی")),
                ("heading_weight", models.PositiveIntegerField(default=500, verbose_name="وزن تیترهای عمومی")),
                ("hero_weight", models.PositiveIntegerField(default=500, verbose_name="وزن تیتر Hero")),
                ("section_weight", models.PositiveIntegerField(default=500, verbose_name="وزن تیتر بخش‌ها")),
                ("card_weight", models.PositiveIntegerField(default=600, verbose_name="وزن تیتر کارت‌ها")),
                ("nav_weight", models.PositiveIntegerField(default=600, verbose_name="وزن منو")),
                ("button_weight", models.PositiveIntegerField(default=700, verbose_name="وزن دکمه‌ها")),
                ("label_weight", models.PositiveIntegerField(default=600, verbose_name="وزن برچسب‌ها")),
                ("small_weight", models.PositiveIntegerField(default=400, verbose_name="وزن متن‌های ریز")),
                ("custom_css", models.TextField(blank=True, help_text="برای سفارشی‌سازی حرفه‌ای. فقط CSS معتبر وارد کنید.", verbose_name="CSS پیشرفته (اختیاری)")),
            ],
            options={"verbose_name": "پوسته و طراحی سایت", "verbose_name_plural": "پوسته و طراحی سایت"},
        ),
    ]
