from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("website", "0003_sitetheme")]

    operations = [
        migrations.AddField(model_name="sitetheme", name="header_background", field=models.CharField(default="rgba(255,255,255,.82)", max_length=60, verbose_name="پس‌زمینه هدر")),
        migrations.AddField(model_name="sitetheme", name="header_opacity", field=models.DecimalField(decimal_places=2, default=0.82, max_digits=3, verbose_name="شفافیت هدر")),
        migrations.AddField(model_name="sitetheme", name="header_blur", field=models.PositiveIntegerField(default=22, verbose_name="Blur هدر (px)")),
        migrations.AddField(model_name="sitetheme", name="header_border", field=models.CharField(default="rgba(9,38,52,.10)", max_length=60, verbose_name="مرز هدر")),
        migrations.AddField(model_name="sitetheme", name="header_text", field=models.CharField(default="#092634", max_length=30, verbose_name="متن هدر")),
        migrations.AddField(model_name="sitetheme", name="header_muted", field=models.CharField(default="#60727D", max_length=30, verbose_name="متن فرعی هدر")),
        migrations.AddField(model_name="sitetheme", name="header_cta_background", field=models.CharField(default="rgba(255,255,255,.62)", max_length=60, verbose_name="پس‌زمینه دکمه مشاوره هدر")),
        migrations.AddField(model_name="sitetheme", name="header_cta_text", field=models.CharField(default="#092634", max_length=30, verbose_name="متن دکمه مشاوره هدر")),
        migrations.AddField(model_name="sitetheme", name="header_cta_border", field=models.CharField(default="rgba(9,38,52,.12)", max_length=60, verbose_name="مرز دکمه مشاوره هدر")),
        migrations.AddField(model_name="sitetheme", name="menu_line_color", field=models.CharField(default="#092634", max_length=30, verbose_name="رنگ خطوط منوی موبایل")),
        migrations.AddField(model_name="sitetheme", name="primary_button_background", field=models.CharField(default="#FF6E42", max_length=30, verbose_name="پس‌زمینه دکمه اصلی")),
        migrations.AddField(model_name="sitetheme", name="primary_button_text", field=models.CharField(default="#081923", max_length=30, verbose_name="متن دکمه اصلی")),
        migrations.AddField(model_name="sitetheme", name="primary_button_hover", field=models.CharField(default="#FF9A7D", max_length=30, verbose_name="Hover دکمه اصلی")),
        migrations.AddField(model_name="sitetheme", name="glass_button_background", field=models.CharField(default="rgba(255,255,255,.10)", max_length=60, verbose_name="پس‌زمینه دکمه شیشه‌ای")),
        migrations.AddField(model_name="sitetheme", name="glass_button_border", field=models.CharField(default="rgba(255,255,255,.28)", max_length=60, verbose_name="مرز دکمه شیشه‌ای")),
        migrations.AddField(model_name="sitetheme", name="modal_background", field=models.CharField(default="rgba(248,249,248,.66)", max_length=60, verbose_name="پس‌زمینه پاپ‌آپ فرم")),
        migrations.AddField(model_name="sitetheme", name="modal_border", field=models.CharField(default="rgba(255,255,255,.92)", max_length=60, verbose_name="مرز پاپ‌آپ فرم")),
        migrations.AddField(model_name="sitetheme", name="footer_background", field=models.CharField(default="#04141E", max_length=60, verbose_name="پس‌زمینه فوتر")),
        migrations.AddField(model_name="sitetheme", name="footer_text", field=models.CharField(default="#FFFFFF", max_length=30, verbose_name="متن فوتر")),
        migrations.AddField(model_name="sitetheme", name="hero_overlay", field=models.CharField(default="rgba(7,29,43,.66)", max_length=100, verbose_name="Overlay تصویر Hero")),
        migrations.AddField(model_name="sitetheme", name="logo_width_desktop", field=models.PositiveIntegerField(default=48, verbose_name="عرض لوگو دسکتاپ (px)")),
        migrations.AddField(model_name="sitetheme", name="logo_width_mobile", field=models.PositiveIntegerField(default=42, verbose_name="عرض لوگو موبایل (px)")),
    ]
