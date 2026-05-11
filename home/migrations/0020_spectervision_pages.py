"""
Specter Vision page models migration.

Adds Specter Vision homepage fields to HomePage and creates all new page types:
StudyIndexPage, StudyPage, ArtifactIndexPage, ArtifactPage, FieldNotesIndexPage,
FieldNotePage, LabPage, WorldPage, CollaboratePage, CollaborateInquiry.

NOTE: StreamField body columns use [] (empty block list) for schema-only compatibility.
Run `python manage.py makemigrations` after deploy to regenerate with full block
serialization if you need migration consistency checking.
"""

import django.db.models.deletion
import modelcluster.fields
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0019_alter_homepage_projects_button_page"),
        ("wagtailcore", "0095_groupsitepermission"),
        ("wagtailimages", "0001_initial"),
    ]

    operations = [
        # ── HomePage: Specter Vision fields ───────────────────────────────────
        migrations.AddField(
            model_name="homepage",
            name="sv_hero_title",
            field=models.CharField(blank=True, default="Specter Vision", max_length=200),
        ),
        migrations.AddField(
            model_name="homepage",
            name="sv_hero_subtitle",
            field=models.CharField(
                blank=True,
                default="Visual studies for a material world.",
                max_length=400,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="sv_hero_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="sv_hero_video_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="homepage",
            name="sv_manifesto_text",
            field=models.TextField(
                blank=True,
                default=(
                    "Specter Vision is the visual studies archive of the Mr. Specter world — "
                    "a cinematic research platform exploring objects, vehicles, people, spaces, "
                    "materials, and the culture around them."
                ),
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="sv_instagram_url",
            field=models.URLField(blank=True, default="https://www.instagram.com/mr.specter007"),
        ),
        migrations.AddField(
            model_name="homepage",
            name="sv_chez_specter_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="homepage",
            name="sv_specter_parts_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="homepage",
            name="sv_cta_label",
            field=models.CharField(blank=True, default="Explore the Studies", max_length=80),
        ),
        migrations.AddField(
            model_name="homepage",
            name="sv_cta_page",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
            ),
        ),

        # ── StudyIndexPage ────────────────────────────────────────────────────
        migrations.CreateModel(
            name="StudyIndexPage",
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
                ("intro_title", models.CharField(blank=True, default="Studies", max_length=200)),
                ("intro_text", models.TextField(blank=True)),
                (
                    "featured_study",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),

        # ── StudyPage ─────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="StudyPage",
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
                ("subtitle", models.CharField(blank=True, max_length=300)),
                ("thesis", models.TextField(blank=True)),
                (
                    "study_type",
                    models.CharField(
                        choices=[
                            ("product", "Product Study"),
                            ("object", "Object Study"),
                            ("automotive", "Automotive Study"),
                            ("material", "Material Study"),
                            ("street", "Street Study"),
                            ("motion", "Motion Study"),
                            ("night", "Night Study"),
                            ("city", "City Study"),
                            ("interior", "Interior Study"),
                            ("field", "Field Study"),
                            ("campaign", "Campaign Study"),
                            ("build", "Build Study"),
                        ],
                        default="field",
                        max_length=30,
                    ),
                ),
                (
                    "hero_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                ("hero_video_url", models.URLField(blank=True)),
                ("date", models.DateField(blank=True, null=True)),
                ("location", models.CharField(blank=True, max_length=200)),
                (
                    "related_brand_area",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("chez_specter", "Chez Specter"),
                            ("specter_parts", "Specter Parts"),
                            ("specter_builds", "Specter Builds"),
                            ("mr_specter_world", "Mr. Specter World"),
                            ("specter_vision", "Specter Vision"),
                        ],
                        max_length=30,
                    ),
                ),
                ("body", wagtail.fields.StreamField([], blank=True, use_json_field=True)),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),

        # ── ArtifactIndexPage ─────────────────────────────────────────────────
        migrations.CreateModel(
            name="ArtifactIndexPage",
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
                ("intro_title", models.CharField(blank=True, default="Artifacts", max_length=200)),
                ("intro_text", models.TextField(blank=True)),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),

        # ── FieldNotesIndexPage ───────────────────────────────────────────────
        migrations.CreateModel(
            name="FieldNotesIndexPage",
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
                ("intro_title", models.CharField(blank=True, default="Field Notes", max_length=200)),
                ("intro_text", models.TextField(blank=True)),
                (
                    "featured_note",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),

        # ── FieldNotePage ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name="FieldNotePage",
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
                ("subtitle", models.CharField(blank=True, max_length=300)),
                (
                    "hero_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("research", "Research"),
                            ("design_direction", "Design Direction"),
                            ("automotive_culture", "Automotive Culture"),
                            ("product_study", "Product Study"),
                            ("material_study", "Material Study"),
                            ("visual_culture", "Visual Culture"),
                            ("street_culture", "Street Culture"),
                            ("event", "Event"),
                            ("build_philosophy", "Build Philosophy"),
                            ("worldbuilding", "Worldbuilding"),
                        ],
                        default="research",
                        max_length=40,
                    ),
                ),
                ("intro", models.TextField(blank=True)),
                ("body", wagtail.fields.StreamField([], blank=True, use_json_field=True)),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),

        # ── ArtifactPage ──────────────────────────────────────────────────────
        migrations.CreateModel(
            name="ArtifactPage",
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
                    "artifact_type",
                    models.CharField(
                        choices=[
                            ("image", "Image"),
                            ("video", "Video"),
                            ("object", "Object"),
                            ("material", "Material"),
                            ("vehicle_detail", "Vehicle Detail"),
                            ("product_detail", "Product Detail"),
                            ("tool", "Tool"),
                            ("space", "Space"),
                            ("street", "Street"),
                            ("portrait", "Portrait"),
                            ("nightlife", "Nightlife"),
                            ("interior", "Interior"),
                            ("signage", "Signage"),
                            ("motion", "Motion"),
                        ],
                        default="image",
                        max_length=30,
                    ),
                ),
                (
                    "hero_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                ("short_caption", models.CharField(blank=True, max_length=400)),
                ("long_description", models.TextField(blank=True)),
                ("date", models.DateField(blank=True, null=True)),
                ("location", models.CharField(blank=True, max_length=200)),
                ("instagram_url", models.URLField(blank=True)),
                ("related_product_reference", models.URLField(blank=True)),
                ("related_platform_reference", models.URLField(blank=True)),
                (
                    "related_study",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="home.studypage",
                    ),
                ),
                (
                    "related_field_note",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="home.fieldnotepage",
                    ),
                ),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),

        # ── StudyPage relation tables ─────────────────────────────────────────
        migrations.CreateModel(
            name="StudyPageRelatedStudy",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_studies",
                        to="home.studypage",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="home.studypage",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        ),
        migrations.CreateModel(
            name="StudyPageRelatedArtifact",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_artifacts",
                        to="home.studypage",
                    ),
                ),
                (
                    "artifact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="home.artifactpage",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        ),
        migrations.CreateModel(
            name="StudyPageRelatedFieldNote",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_field_notes",
                        to="home.studypage",
                    ),
                ),
                (
                    "note",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="home.fieldnotepage",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        ),

        # ── ArtifactPageGalleryImage ──────────────────────────────────────────
        migrations.CreateModel(
            name="ArtifactPageGalleryImage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                ("caption", models.CharField(blank=True, max_length=255)),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="gallery_images",
                        to="home.artifactpage",
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        ),

        # ── FieldNote relation tables ─────────────────────────────────────────
        migrations.CreateModel(
            name="FieldNoteRelatedStudy",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_studies",
                        to="home.fieldnotepage",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="home.studypage",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        ),
        migrations.CreateModel(
            name="FieldNoteRelatedArtifact",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_artifacts",
                        to="home.fieldnotepage",
                    ),
                ),
                (
                    "artifact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="home.artifactpage",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        ),

        # ── LabPage ───────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="LabPage",
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
                ("intro_title", models.CharField(blank=True, default="The Lab", max_length=200)),
                (
                    "intro_text",
                    models.TextField(
                        blank=True,
                        default=(
                            "Experiments, visual tests, prototypes, and unfinished research. "
                            "The Lab is where Specter Vision works in the open."
                        ),
                    ),
                ),
                ("body", wagtail.fields.StreamField([], blank=True, use_json_field=True)),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),

        # ── WorldPage ─────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="WorldPage",
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
                    "hero_title",
                    models.CharField(blank=True, default="Mr. Specter World", max_length=200),
                ),
                (
                    "hero_text",
                    models.TextField(
                        blank=True,
                        default=(
                            "Mr. Specter is a world of objects, vehicles, tools, images, and systems. "
                            "Chez Specter carries the objects. Specter Parts powers the sourcing. "
                            "Specter Vision carries the story."
                        ),
                    ),
                ),
                ("body", wagtail.fields.StreamField([], blank=True, use_json_field=True)),
                ("chez_specter_url", models.URLField(blank=True)),
                ("specter_parts_url", models.URLField(blank=True)),
                (
                    "instagram_url",
                    models.URLField(
                        blank=True, default="https://www.instagram.com/mr.specter007"
                    ),
                ),
                ("future_builds_text", models.TextField(blank=True)),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),

        # ── CollaboratePage ───────────────────────────────────────────────────
        migrations.CreateModel(
            name="CollaboratePage",
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
                    "intro_title",
                    models.CharField(blank=True, default="Collaborate", max_length=200),
                ),
                (
                    "intro_text",
                    models.TextField(
                        blank=True,
                        default=(
                            "Specter Vision is open to meaningful creative and strategic work. "
                            "Propose a study, commission a visual essay, or initiate a collaboration "
                            "that belongs in this world."
                        ),
                    ),
                ),
                (
                    "success_message",
                    models.CharField(
                        default="Your inquiry has been received. We will be in touch.",
                        max_length=255,
                    ),
                ),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),

        # ── CollaborateInquiry ────────────────────────────────────────────────
        migrations.CreateModel(
            name="CollaborateInquiry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                (
                    "inquiry_type",
                    models.CharField(
                        choices=[
                            ("product_study", "Product Study"),
                            ("automotive_study", "Automotive Study"),
                            ("editorial", "Editorial / Publication"),
                            ("exhibition", "Exhibition / Event"),
                            ("brand_collab", "Brand Collaboration"),
                            ("object_documentation", "Object Documentation"),
                            ("visual_direction", "Visual Direction"),
                            ("other", "Other"),
                        ],
                        max_length=40,
                    ),
                ),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inquiries",
                        to="home.collaboratepage",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "verbose_name_plural": "Collaborate inquiries",
            },
        ),
    ]
