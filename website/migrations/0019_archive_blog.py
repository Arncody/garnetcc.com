from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("website", "0018_home_presentation")]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Archive the table and all rows so this feature removal is reversible.
            database_operations=[
                migrations.AlterModelTable(name="blogpost", table="website_retired_blogpost"),
            ],
            state_operations=[migrations.DeleteModel(name="BlogPost")],
        ),
    ]
