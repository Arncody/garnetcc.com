from django.db import migrations, models
from website.models import IMAGE_VALIDATORS


class Migration(migrations.Migration):
    dependencies = [("website", "0007_brand_logo_project_info")]
    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="logo_light",
            field=models.ImageField(
                blank=True, upload_to="site/", validators=IMAGE_VALIDATORS,
                help_text="هدر سایت شیشه‌ای و تیره است؛ اگر متن لوگوی شما تیره است، نسخه‌ای با متن سفید/روشن اینجا آپلود کنید. در نبود آن، همان لوگوی اصلی نمایش داده می‌شود.",
                verbose_name="لوگوی نسخه روشن برای هدر (اختیاری)",
            ),
        ),
    ]
