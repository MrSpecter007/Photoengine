from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0012_adminexperiencesettings_sidebar_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="adminexperiencesettings",
            name="admin_sidebar_text_color",
            field=models.CharField(
                default="#F8F7FB",
                help_text="Text color used for sidebar navigation labels and icons.",
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Enter a valid hex color like #DA0D2B.",
                        regex="^#[0-9A-Fa-f]{6}$",
                    )
                ],
            ),
        ),
        migrations.AddField(
            model_name="adminexperiencesettings",
            name="admin_text_color",
            field=models.CharField(
                default="#101418",
                help_text="Main text color for custom admin welcome content and dashboard accents.",
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
