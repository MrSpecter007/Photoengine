from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0019_alter_homepage_projects_button_page"),
        ("wagtailcore", "0095_groupsitepermission"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="AboutPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("about_eyebrow", models.CharField(default="about", max_length=80)),
                (
                    "about_heading",
                    models.TextField(
                        default="I'm Michel Groch,\nA Professional Photographer\nLiving In Indonesia."
                    ),
                ),
                (
                    "about_paragraph_one",
                    models.TextField(
                        default=(
                            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
                            "tempor incididunt ut labore et dolore magna aliqua."
                        )
                    ),
                ),
                (
                    "about_paragraph_two",
                    models.TextField(
                        default=(
                            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                            "aliquip ex ea commodo consequat duis."
                        )
                    ),
                ),
                (
                    "about_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
    ]
