from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("website", "0021_project_search_and_catalog_visibility")]

    operations = [
        migrations.AddField(
            model_name="sitetexts",
            name="interface_copy",
            field=models.JSONField(blank=True, default=dict, editable=False),
        ),
    ]
