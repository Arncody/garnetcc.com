import django.db.models.deletion
from django.db import migrations, models

PROJECT_SUBMENU = [
    # (عنوان, عنوان EN, لینک, ترتیب)
    ("در حال اجرا", "In progress", "/projects/#ongoing", 1),
    ("تمام‌شده", "Completed", "/projects/#completed", 2),
]


def seed_projects_submenu(apps, schema_editor):
    """به آیتم منوی «پروژه‌ها» (لینک /projects/) دو زیرمنوی پیش‌فرض اضافه می‌کند؛ اگر قبلاً زیرمنو دارد دست نمی‌زند."""
    MenuItem = apps.get_model("website", "MenuItem")
    MenuSubItem = apps.get_model("website", "MenuSubItem")
    for item in MenuItem.objects.all():
        base = (item.url or "").strip().split("#", 1)[0].split("?", 1)[0]
        if item.open_consult or base.rstrip("/") != "/projects":
            continue
        if MenuSubItem.objects.filter(parent=item).exists():
            continue
        for title, title_en, url, order in PROJECT_SUBMENU:
            MenuSubItem.objects.create(parent=item, title=title, title_en=title_en, url=url, order=order)


class Migration(migrations.Migration):
    dependencies = [("website", "0013_newsletter_and_consult_button_text")]

    operations = [
        migrations.AddField(
            model_name="sitetheme",
            name="color_overrides",
            field=models.JSONField(
                blank=True, default=dict, editable=False,
                verbose_name="رنگ‌های سفارشی اجزای سایت",
                help_text="فقط رنگ‌هایی که از پنل «رنگ اجزای سایت» تغییر داده شده‌اند (کلید → رنگ). فیلد خالی = ظاهر پیش‌فرض.",
            ),
        ),
        migrations.CreateModel(
            name="MenuSubItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=60, verbose_name="عنوان")),
                ("title_en", models.CharField(blank=True, max_length=60, verbose_name="عنوان (EN)")),
                ("url", models.CharField(
                    max_length=200, verbose_name="لینک",
                    help_text="مثال: /projects/#ongoing یا /projects/#completed",
                )),
                ("order", models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")),
                ("is_active", models.BooleanField(default=True, verbose_name="نمایش در زیرمنو")),
                ("parent", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name="children",
                    to="website.menuitem", verbose_name="آیتم والد",
                )),
            ],
            options={"verbose_name": "زیرمنو", "verbose_name_plural": "زیرمنوها", "ordering": ["order", "id"]},
        ),
        migrations.RunPython(seed_projects_submenu, migrations.RunPython.noop),
    ]
