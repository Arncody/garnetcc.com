from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models

DEFAULT_MENU = [
    # (عنوان, عنوان EN, لینک, باز شدن فرم مشاوره, ترتیب)
    ("صفحه اصلی", "Home", "/", False, 1),
    ("پروژه‌ها", "Projects", "/projects/", False, 2),
    ("درباره گارنت", "About Garnet", "/#about", False, 3),
    ("همکاری با گارنت", "Work with Garnet", "", True, 4),
    ("مقالات و اخبار", "Articles & News", "/blog/", False, 5),
    ("تماس با ما", "Contact us", "#contact", False, 6),
]


def seed_menu(apps, schema_editor):
    MenuItem = apps.get_model("website", "MenuItem")
    if MenuItem.objects.exists():
        return
    for title, title_en, url, consult, order in DEFAULT_MENU:
        MenuItem.objects.create(title=title, title_en=title_en, url=url, open_consult=consult, order=order)


class Migration(migrations.Migration):
    dependencies = [("website", "0011_favicon")]
    operations = [
        migrations.AddField(
            model_name="sitesettings", name="linkedin_url",
            field=models.URLField(
                blank=True, default="", verbose_name="لینک لینکدین",
                help_text="در فوتر سایت کنار اینستاگرام نمایش داده می‌شود؛ اگر خالی بماند، نمایش داده نمی‌شود.",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings", name="projects_carousel_enabled",
            field=models.BooleanField(
                default=True, verbose_name="چرخش افقی خودکار پروژه‌ها",
                help_text="اگر خاموش شود، پروژه‌ها به‌صورت ردیف/شبکه‌ی ثابت نمایش داده می‌شوند.",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings", name="projects_carousel_speed",
            field=models.PositiveIntegerField(
                default=40, validators=[MinValueValidator(10), MaxValueValidator(200)],
                verbose_name="سرعت چرخش پروژه‌ها (پیکسل بر ثانیه)",
                help_text="عدد بین ۱۰ تا ۲۰۰؛ مقدار استاندارد ۴۰ است (بزرگ‌تر = سریع‌تر).",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings", name="projects_carousel_on_list",
            field=models.BooleanField(default=True, verbose_name="چرخش پروژه‌ها در صفحه «پروژه‌ها» هم اعمال شود"),
        ),
        migrations.CreateModel(
            name="MenuItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=60, verbose_name="عنوان")),
                ("title_en", models.CharField(blank=True, max_length=60, verbose_name="عنوان (EN)")),
                ("url", models.CharField(
                    blank=True, default="", max_length=200, verbose_name="لینک",
                    help_text="مثال: /projects/ یا /#about یا #contact (رفتن به فوتر). برای باز شدن فرم مشاوره، گزینه‌ی پایین را تیک بزنید.",
                )),
                ("open_consult", models.BooleanField(default=False, verbose_name="باز کردن فرم مشاوره به‌جای رفتن به لینک")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")),
                ("is_active", models.BooleanField(default=True, verbose_name="نمایش در منو")),
            ],
            options={"verbose_name": "آیتم منو", "verbose_name_plural": "آیتم‌های منوی اصلی", "ordering": ["order", "id"]},
        ),
        migrations.RunPython(seed_menu, migrations.RunPython.noop),
    ]
