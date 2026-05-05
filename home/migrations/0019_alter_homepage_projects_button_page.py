from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0095_groupsitepermission"),
        ("home", "0018_remove_homepage_projects_button_link"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepage",
            name="projects_button_page",
            field=models.ForeignKey(
                blank=True,
                help_text="Select an existing portfolio page or gallery to open from the homepage button.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
            ),
        ),
    ]
