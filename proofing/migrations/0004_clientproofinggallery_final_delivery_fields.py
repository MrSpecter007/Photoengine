from django.db import migrations, models


def copy_legacy_delivery_fields(apps, schema_editor):
    ClientProofingGallery = apps.get_model("proofing", "ClientProofingGallery")
    for gallery in ClientProofingGallery.objects.all():
        changed = False

        if gallery.download_link_high_res and not gallery.final_delivery_url:
            gallery.final_delivery_url = gallery.download_link_high_res
            changed = True

        if gallery.delivery_notes and not gallery.final_delivery_note:
            gallery.final_delivery_note = gallery.delivery_notes
            changed = True

        if gallery.final_delivery_url and gallery.final_delivery_status == "not_ready":
            gallery.final_delivery_status = "ready"
            changed = True

        if changed:
            gallery.save(
                update_fields=[
                    "final_delivery_url",
                    "final_delivery_note",
                    "final_delivery_status",
                ]
            )


class Migration(migrations.Migration):

    dependencies = [
        ("proofing", "0003_clientproofinggallery_presentation_style"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientproofinggallery",
            name="final_delivery_access_note",
            field=models.CharField(
                blank=True,
                help_text="Optional client-facing note such as 'Password sent separately'.",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="clientproofinggallery",
            name="final_delivery_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="clientproofinggallery",
            name="final_delivery_note",
            field=models.TextField(
                blank=True,
                help_text="Optional client-facing note about the final delivery.",
            ),
        ),
        migrations.AddField(
            model_name="clientproofinggallery",
            name="final_delivery_provider",
            field=models.CharField(
                blank=True,
                choices=[
                    ("wetransfer", "WeTransfer"),
                    ("dropbox", "Dropbox"),
                    ("google_drive", "Google Drive"),
                    ("other", "Other"),
                ],
                default="wetransfer",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="clientproofinggallery",
            name="final_delivery_status",
            field=models.CharField(
                choices=[
                    ("not_ready", "Not ready"),
                    ("ready", "Ready"),
                    ("sent", "Sent"),
                    ("expired", "Expired"),
                    ("archived", "Archived"),
                ],
                default="not_ready",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="clientproofinggallery",
            name="final_delivery_url",
            field=models.URLField(
                blank=True,
                help_text=(
                    "External delivery link for final high-resolution files. "
                    "Do not upload final originals into PhotoEngine."
                ),
            ),
        ),
        migrations.RunPython(
            copy_legacy_delivery_fields,
            migrations.RunPython.noop,
        ),
    ]
