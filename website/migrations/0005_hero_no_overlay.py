from django.db import migrations, models


def clear_overlay(apps, schema_editor):
    SiteTheme = apps.get_model("website", "SiteTheme")
    SiteTheme.objects.update(hero_overlay="transparent")


class Migration(migrations.Migration):
    dependencies = [("website", "0004_advanced_theme_controls")]
    operations = [
        migrations.AlterField(model_name="sitetheme", name="hero_overlay", field=models.CharField(default="transparent", max_length=100, verbose_name="Overlay تصویر Hero (غیرفعال — تصویر/ویدیو بدون کاور نمایش داده می‌شود)")),
        migrations.RunPython(clear_overlay, migrations.RunPython.noop),
    ]
