from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0013_adminexperiencesettings_font_colors"),
    ]

    operations = [
        migrations.AddField(
            model_name="adminexperiencesettings",
            name="admin_sidebar_reverse_hover",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "When enabled, sidebar hover and active states invert the sidebar and text "
                    "colors instead of using the primary accent color."
                ),
            ),
        ),
    ]
