from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proofing", "0002_client_clientproofinggallery_client_notes_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientproofinggallery",
            name="presentation_style",
            field=models.CharField(
                choices=[
                    ("default", "Default"),
                    ("grid", "Grid (Standard)"),
                    ("masonry", "Masonry"),
                    ("animate-scroll-1", "Animate Scroll 1"),
                    ("animate-scroll-3", "Animate Scroll 3"),
                    ("gallery-carousel-1", "Gallery Carousel 1"),
                    ("gallery-carousel-2", "Gallery Carousel 2"),
                ],
                default="default",
                max_length=32,
            ),
        ),
    ]
