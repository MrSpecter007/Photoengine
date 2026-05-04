from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import wagtail.contrib.settings.models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0010_bootstrap_french_locale"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminExperienceSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "admin_brand_name",
                    models.CharField(
                        default="Naji Photo Studio",
                        help_text="Short name used for the Wagtail admin experience.",
                        max_length=80,
                    ),
                ),
                (
                    "admin_welcome_title",
                    models.CharField(
                        default="Welcome back to the studio",
                        help_text="Headline shown on the admin dashboard.",
                        max_length=120,
                    ),
                ),
                (
                    "admin_welcome_message",
                    models.TextField(
                        default="Use this workspace to publish galleries, manage inquiries, and keep client projects moving with confidence.",
                        help_text="A short dashboard message to make the admin feel personal and familiar.",
                    ),
                ),
                (
                    "admin_primary_color",
                    models.CharField(
                        default="#DA0D2B",
                        help_text="Primary action color for buttons and highlights.",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid hex color like #DA0D2B.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "admin_surface_color",
                    models.CharField(
                        default="#1B1B1B",
                        help_text="Dark surface color used for the admin chrome.",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid hex color like #DA0D2B.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "admin_soft_color",
                    models.CharField(
                        default="#F6E8EC",
                        help_text="Soft tint used for cards, focus states, and welcome accents.",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid hex color like #DA0D2B.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "admin_logo",
                    models.ForeignKey(
                        blank=True,
                        help_text="Optional square or compact mark used in the custom admin welcome panel.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "verbose_name": "Admin Experience",
            },
            bases=(wagtail.contrib.settings.models.BaseGenericSetting, models.Model),
        ),
    ]
