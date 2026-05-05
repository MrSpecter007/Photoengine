from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0017_remove_homepage_signature_image"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="homepage",
            name="projects_button_link",
        ),
    ]
