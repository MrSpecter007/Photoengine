from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0006_gallerypage_presentation_style"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "contact_heading",
                    models.CharField(default="In Case You Need Photos", max_length=120),
                ),
                (
                    "contact_detail_heading",
                    models.CharField(default="Contact Detail", max_length=120),
                ),
                (
                    "contact_phone",
                    models.CharField(blank=True, default="(0) 6452 2711 22", max_length=50),
                ),
                (
                    "contact_email",
                    models.EmailField(blank=True, default="michelgroch@support.com", max_length=254),
                ),
                (
                    "address_heading",
                    models.CharField(default="Address", max_length=120),
                ),
                (
                    "address_text",
                    models.TextField(blank=True, default="Lokgebouw 226 5617AC, Eindhoven\nThe Netherlands"),
                ),
                (
                    "form_heading",
                    models.CharField(default="Tell Me About Your Shoot", max_length=120),
                ),
                (
                    "form_intro",
                    models.TextField(
                        blank=True,
                        default="Share a few details and I will get back to you with availability, pricing, and next steps.",
                    ),
                ),
                (
                    "success_message",
                    models.CharField(
                        default="Thanks for reaching out. Your inquiry has been received.",
                        max_length=255,
                    ),
                ),
                (
                    "contact_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="ContactInquiry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone_number", models.CharField(max_length=40)),
                ("photography_type", models.CharField(max_length=40)),
                ("desired_start_date", models.DateField()),
                ("desired_end_date", models.DateField()),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inquiries",
                        to="home.contactpage",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
