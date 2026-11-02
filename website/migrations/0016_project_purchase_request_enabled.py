# Generated for project purchase-request visibility toggle.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0015_project_catalog_and_button_labels"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="purchase_request_enabled",
            field=models.BooleanField(
                default=True,
                help_text="برای پروژه‌هایی که فروش آن‌ها تمام شده یا درخواست خرید موقتاً بسته است، غیرفعال کنید. نمایش پروژه و کاتالوگ مستقل می‌ماند.",
                verbose_name="فعال بودن دکمه درخواست خرید",
            ),
        ),
    ]
