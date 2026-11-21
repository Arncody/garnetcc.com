from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("website", "0016_project_purchase_request_enabled")]

    operations = [
        migrations.AddField(
            model_name="sitetexts",
            name="home_projects_title",
            field=models.CharField("عنوان بخش پروژه‌های صفحه اصلی", max_length=120, blank=True, default="گارنت، در یک نگاه."),
        ),
        migrations.AddField(
            model_name="sitetexts",
            name="home_projects_title_en",
            field=models.CharField("عنوان بخش پروژه‌های صفحه اصلی (EN)", max_length=120, blank=True, default="A clear view of Garnet."),
        ),
        migrations.AddField(
            model_name="sitetexts",
            name="project_view_button",
            field=models.CharField("متن دکمه مشاهده پروژه", max_length=80, blank=True, default="مشاهده پروژه"),
        ),
        migrations.AddField(
            model_name="sitetexts",
            name="project_view_button_en",
            field=models.CharField("متن دکمه مشاهده پروژه (EN)", max_length=80, blank=True, default="View project"),
        ),
        migrations.AddField(
            model_name="sitetexts",
            name="footer_purchase_button",
            field=models.CharField("متن دکمه درخواست خرید فوتر", max_length=120, blank=True, default="درخواست خرید"),
        ),
        migrations.AddField(
            model_name="sitetexts",
            name="footer_purchase_button_en",
            field=models.CharField("متن دکمه درخواست خرید فوتر (EN)", max_length=120, blank=True, default="Request to buy"),
        ),
    ]
