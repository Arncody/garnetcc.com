from django.db import migrations, models
import website.models


class Migration(migrations.Migration):
    dependencies = [("website", "0014_theme_colors_submenu")]

    operations = [
        migrations.AddField(
            model_name="project",
            name="catalog_file",
            field=models.FileField(blank=True, help_text="فایل PDF اختصاصی همین پروژه؛ حداکثر ۲۰ مگابایت. در صورت خالی بودن، دکمه کاتالوگ نمایش داده نمی‌شود.", upload_to="projects/catalogs/", validators=website.models.PDF_VALIDATORS, verbose_name="کاتالوگ PDF پروژه"),
        ),
        migrations.AddField(
            model_name="sitetexts",
            name="project_catalog_button_text",
            field=models.CharField(blank=True, default="کاتالوگ پروژه", max_length=80, verbose_name="عنوان دکمه کاتالوگ پروژه"),
        ),
        migrations.AddField(
            model_name="sitetexts",
            name="project_catalog_button_text_en",
            field=models.CharField(blank=True, default="Project catalog", max_length=80, verbose_name="عنوان دکمه کاتالوگ پروژه (EN)"),
        ),
    ]
