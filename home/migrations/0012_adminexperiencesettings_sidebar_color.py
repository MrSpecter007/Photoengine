from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0011_adminexperiencesettings"),
    ]

    operations = [
        migrations.AddField(
            model_name="adminexperiencesettings",
            name="admin_sidebar_color",
            field=models.CharField(
                default="#241A33",
                help_text="Sidebar color used for Wagtail navigation and menu states.",
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Enter a valid hex color like #DA0D2B.",
                        regex="^#[0-9A-Fa-f]{6}$",
                    )
                ],
            ),
        ),
    ]
