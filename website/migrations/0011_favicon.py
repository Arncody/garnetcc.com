from django.db import migrations, models
from website.models import IMAGE_VALIDATORS


class Migration(migrations.Migration):
    dependencies = [("website", "0010_all_projects_button_text")]
    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="favicon",
            field=models.ImageField(
                blank=True, upload_to="site/", validators=IMAGE_VALIDATORS,
                help_text="فقط نماد/آرم شرکت (بدون نوشته) به‌صورت مربع، PNG، حداقل 512×512 پیکسل. گوگل فقط آیکون‌های مربعی با اندازه مضرب 48 پیکسل را نمایش می‌دهد.",
                verbose_name="فاویکون (آیکون تب مرورگر و گوگل)",
            ),
        ),
    ]
