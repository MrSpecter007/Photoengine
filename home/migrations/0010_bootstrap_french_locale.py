from django.db import migrations


def bootstrap_french_locale(apps, schema_editor):
    from wagtail.models import Locale

    # Ensure en locale exists and fr locale is registered.
    # Page-copying is skipped: on a fresh install the HomePage model is ahead of
    # the migration state (projects_button_page_id doesn't exist yet), so calling
    # .specific would abort the PostgreSQL transaction.
    Locale.objects.filter(language_code="en-us").update(language_code="en")
    Locale.objects.get_or_create(language_code="en")
    Locale.objects.get_or_create(language_code="fr")


class Migration(migrations.Migration):
    dependencies = [
        ("proofing", "0003_clientproofinggallery_presentation_style"),
        ("home", "0009_alter_homepage_projects_button_text_and_more"),
    ]

    operations = [
        migrations.RunPython(bootstrap_french_locale, migrations.RunPython.noop),
    ]
