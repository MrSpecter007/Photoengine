from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0016_homepage_projects_button_page"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="homepage",
            name="signature_image",
        ),
    ]
