from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("website", "0009_remove_services_showcase_texts")]
    operations = [
        migrations.AddField(
            model_name="sitetexts", name="all_projects_btn",
            field=models.CharField(blank=True, default="مشاهده همه پروژه‌ها", max_length=250, verbose_name="متن دکمه «مشاهده همه پروژه‌ها»"),
        ),
        migrations.AddField(
            model_name="sitetexts", name="all_projects_btn_en",
            field=models.CharField(blank=True, default="View all projects", max_length=250, verbose_name="متن دکمه «مشاهده همه پروژه‌ها» (EN)"),
        ),
    ]
