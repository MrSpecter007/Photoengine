from django.db import migrations


def bootstrap_french_locale(apps, schema_editor):
    from django.db import transaction
    from wagtail.models import Locale, Site

    Locale.objects.filter(language_code="en-us").update(language_code="en")
    Locale.objects.get_or_create(language_code="en")
    french_locale, _ = Locale.objects.get_or_create(language_code="fr")

    # .specific loads the live model class, which may reference columns not yet
    # added (e.g. projects_button_page_id from migration 0016). Wrap in a
    # savepoint so a failed query only aborts the inner block and the outer
    # migration transaction remains healthy.
    for site in Site.objects.select_related("root_page"):
        try:
            with transaction.atomic():
                root_page = site.root_page.specific
                pages = [root_page] + list(
                    root_page.get_descendants().specific().order_by("path")
                )
        except Exception:
            continue

        for page in pages:
            if page.locale_id == french_locale.id:
                continue

            existing_translation = page.get_translations().filter(locale=french_locale).first()
            if existing_translation is not None:
                if page.live and not existing_translation.live:
                    existing_translation.save_revision().publish()
                continue

            try:
                with transaction.atomic():
                    translated_page = page.copy_for_translation(french_locale, copy_parents=True)
                    if page.live:
                        translated_page.save_revision().publish()
            except Exception:
                pass


class Migration(migrations.Migration):
    dependencies = [
        ("proofing", "0003_clientproofinggallery_presentation_style"),
        ("home", "0009_alter_homepage_projects_button_text_and_more"),
    ]

    operations = [
        migrations.RunPython(bootstrap_french_locale, migrations.RunPython.noop),
    ]
