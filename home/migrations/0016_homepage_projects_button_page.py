from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0095_groupsitepermission"),
        ("home", "0015_adminexperiencesettings_sidebar_state_colors"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="projects_button_page",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
            ),
        ),
    ]
