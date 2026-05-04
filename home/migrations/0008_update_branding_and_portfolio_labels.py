from django.db import migrations


def update_homepage_portfolio_labels(apps, schema_editor):
    HomePage = apps.get_model("home", "HomePage")

    for homepage in HomePage.objects.all():
        changed_fields = []

        if homepage.projects_eyebrow == "Projects":
            homepage.projects_eyebrow = "Portfolio"
            changed_fields.append("projects_eyebrow")

        if homepage.projects_button_text == "view projects":
            homepage.projects_button_text = "view portfolio"
            changed_fields.append("projects_button_text")

        if changed_fields:
            homepage.save(update_fields=changed_fields)


def revert_homepage_portfolio_labels(apps, schema_editor):
    HomePage = apps.get_model("home", "HomePage")

    for homepage in HomePage.objects.all():
        changed_fields = []

        if homepage.projects_eyebrow == "Portfolio":
            homepage.projects_eyebrow = "Projects"
            changed_fields.append("projects_eyebrow")

        if homepage.projects_button_text == "view portfolio":
            homepage.projects_button_text = "view projects"
            changed_fields.append("projects_button_text")

        if changed_fields:
            homepage.save(update_fields=changed_fields)


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0007_contactpage_contactinquiry"),
    ]

    operations = [
        migrations.RunPython(
            update_homepage_portfolio_labels,
            revert_homepage_portfolio_labels,
        ),
    ]
