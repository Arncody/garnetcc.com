from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("website", "0012_menu_linkedin_carousel")]

    operations = [
        migrations.AddField(
            model_name="sitetexts",
            name="consultation_button_text",
            field=models.CharField(blank=True, default="درخواست مشاوره", max_length=120, verbose_name="متن دکمه درخواست مشاوره در سراسر سایت"),
        ),
        migrations.AddField(
            model_name="sitetexts",
            name="consultation_button_text_en",
            field=models.CharField(blank=True, default="Request consultation", max_length=120, verbose_name="متن دکمه درخواست مشاوره در سراسر سایت (EN)"),
        ),
        migrations.CreateModel(
            name="NewsletterSubscriber",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="ایمیل")),
                ("is_active", models.BooleanField(default=True, verbose_name="عضویت فعال")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ عضویت")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")),
            ],
            options={
                "verbose_name": "عضو خبرنامه",
                "verbose_name_plural": "اعضای خبرنامه",
                "ordering": ["-created_at"],
            },
        ),
    ]
