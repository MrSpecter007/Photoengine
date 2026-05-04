from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0008_update_branding_and_portfolio_labels"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepage",
            name="projects_button_text",
            field=models.CharField(default="view portfolio", max_length=80),
        ),
        migrations.AlterField(
            model_name="homepage",
            name="projects_eyebrow",
            field=models.CharField(default="Portfolio", max_length=80),
        ),
    ]
