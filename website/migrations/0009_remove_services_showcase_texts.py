from django.db import migrations


class Migration(migrations.Migration):
    """حذف کامل بخش خدمات و دو متن قدیمی «نمونه‌کار + بلاگ» (جایگزین شده‌اند)."""
    dependencies = [("website", "0008_logo_light")]
    operations = [
        migrations.DeleteModel(name="ServiceImage"),
        migrations.DeleteModel(name="Service"),
        migrations.RemoveField(model_name="sitetexts", name="showcase_eyebrow"),
        migrations.RemoveField(model_name="sitetexts", name="showcase_eyebrow_en"),
        migrations.RemoveField(model_name="sitetexts", name="showcase_title"),
        migrations.RemoveField(model_name="sitetexts", name="showcase_title_en"),
    ]
