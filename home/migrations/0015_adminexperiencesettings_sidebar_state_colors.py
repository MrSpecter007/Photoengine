from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0014_adminexperiencesettings_sidebar_reverse_hover"),
    ]

    operations = [
        migrations.AddField(
            model_name="adminexperiencesettings",
            name="admin_sidebar_hover_color",
            field=models.CharField(
                default="#000000",
                help_text="Sidebar menu background color on hover.",
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
            name="admin_sidebar_hover_text_color",
            field=models.CharField(
                default="#FFFFFF",
                help_text="Sidebar menu text and icon color on hover.",
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
            name="admin_sidebar_selected_color",
            field=models.CharField(
                default="#000000",
                help_text="Sidebar menu background color for the selected item.",
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
            name="admin_sidebar_selected_text_color",
            field=models.CharField(
                default="#FFFFFF",
                help_text="Sidebar menu text and icon color for the selected item.",
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Enter a valid hex color like #DA0D2B.",
                        regex="^#[0-9A-Fa-f]{6}$",
                    )
                ],
            ),
        ),
        migrations.RemoveField(
            model_name="adminexperiencesettings",
            name="admin_sidebar_reverse_hover",
        ),
    ]
