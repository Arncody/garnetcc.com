from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="herosection",
            name="background_video",
            field=models.FileField(
                blank=True,
                help_text="MP4/WebM ترجیحاً 1920×1080، حجم پیشنهادی حداکثر 15MB.",
                upload_to="hero/videos/",
            ),
        ),
        migrations.CreateModel(
            name="CompanyCatalog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(default="کاتالوگ شرکت", max_length=150, verbose_name="عنوان کاتالوگ")),
                ("title_en", models.CharField(blank=True, default="Company Catalog", max_length=150, verbose_name="عنوان کاتالوگ (EN)")),
                ("file", models.FileField(upload_to="catalogs/", verbose_name="فایل کاتالوگ")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")),
            ],
            options={
                "verbose_name": "کاتالوگ شرکت",
                "verbose_name_plural": "کاتالوگ شرکت",
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="BlogPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=220, verbose_name="عنوان")),
                ("title_en", models.CharField(blank=True, max_length=220, verbose_name="عنوان (EN)")),
                ("slug", models.SlugField(max_length=240, unique=True, verbose_name="Slug")),
                ("excerpt", models.TextField(blank=True, max_length=500, verbose_name="خلاصه")),
                ("excerpt_en", models.TextField(blank=True, max_length=500, verbose_name="خلاصه (EN)")),
                ("content", models.TextField(verbose_name="متن مقاله")),
                ("content_en", models.TextField(blank=True, verbose_name="متن مقاله (EN)")),
                ("cover", models.ImageField(blank=True, upload_to="blog/", verbose_name="تصویر کاور")),
                ("seo_title", models.CharField(blank=True, max_length=70, verbose_name="عنوان SEO")),
                ("seo_title_en", models.CharField(blank=True, max_length=70, verbose_name="عنوان SEO (EN)")),
                ("seo_description", models.CharField(blank=True, max_length=160, verbose_name="توضیحات SEO")),
                ("seo_description_en", models.CharField(blank=True, max_length=160, verbose_name="توضیحات SEO (EN)")),
                ("category", models.CharField(default="معماری", max_length=100, verbose_name="دسته‌بندی")),
                ("category_en", models.CharField(blank=True, default="Architecture", max_length=100, verbose_name="دسته‌بندی (EN)")),
                ("is_published", models.BooleanField(default=False, verbose_name="منتشر شود")),
                ("is_featured", models.BooleanField(default=False, verbose_name="مقاله ویژه")),
                ("published_at", models.DateTimeField(blank=True, null=True, verbose_name="تاریخ انتشار")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "مقاله وبلاگ",
                "verbose_name_plural": "مقالات وبلاگ",
                "ordering": ["-published_at", "-created_at"],
            },
        ),
    ]
