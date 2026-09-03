from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PhotoCollection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, unique=True)),
                ("code", models.SlugField(blank=True, max_length=32, unique=True)),
                ("description", models.TextField(blank=True)),
                ("launch_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"verbose_name": "Photo Collection", "verbose_name_plural": "Photo Collections", "ordering": ["title"]},
        ),
        migrations.CreateModel(
            name="EditionFormat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(unique=True)),
                ("name", models.CharField(max_length=100)),
                ("short_description", models.CharField(blank=True, max_length=255)),
                ("long_description", models.TextField(blank=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"verbose_name": "Edition Format", "verbose_name_plural": "Edition Formats", "ordering": ["sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="PrintSize",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("aspect_ratio", models.CharField(max_length=20)),
                ("width_in", models.DecimalField(decimal_places=2, max_digits=6)),
                ("height_in", models.DecimalField(decimal_places=2, max_digits=6)),
                ("label", models.CharField(max_length=50)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={"verbose_name": "Print Size", "verbose_name_plural": "Print Sizes", "ordering": ["aspect_ratio", "sort_order", "width_in", "height_in"]},
        ),
        migrations.AddConstraint(
            model_name="printsize",
            constraint=models.UniqueConstraint(fields=["aspect_ratio", "width_in", "height_in"], name="editions_printsize_unique"),
        ),
        migrations.CreateModel(
            name="Photograph",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("collection", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="photographs", to="editions.photocollection")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True)),
                ("code", models.SlugField(blank=True, max_length=32)),
                ("location_name", models.CharField(blank=True, max_length=200)),
                ("story", models.TextField(blank=True)),
                ("edition_details_text", models.TextField(blank=True)),
                ("native_ratio", models.CharField(blank=True, help_text="e.g. 3:2 or 4:5", max_length=10)),
                ("image", models.ImageField(blank=True, null=True, upload_to="editions/photographs/")),
                ("hero_image", models.ImageField(blank=True, null=True, upload_to="editions/heroes/")),
                ("public_edition_size", models.PositiveIntegerField(default=5)),
                ("artist_proof_size", models.PositiveIntegerField(default=2)),
                ("available_as_portrait", models.BooleanField(default=True)),
                ("available_as_landscape", models.BooleanField(default=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_sold_out", models.BooleanField(default=False)),
                ("is_preorder", models.BooleanField(default=False)),
            ],
            options={"verbose_name": "Photograph", "verbose_name_plural": "Photographs", "ordering": ["collection__title", "title"]},
        ),
        migrations.AddConstraint(
            model_name="photograph",
            constraint=models.UniqueConstraint(fields=["collection", "slug"], name="editions_photograph_unique_collection_slug"),
        ),
        migrations.CreateModel(
            name="PhotographEdition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("photograph", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="editions", to="editions.photograph")),
                ("edition_type", models.CharField(choices=[("public", "Public Edition"), ("artist_proof", "Artist Proof")], max_length=30)),
                ("number", models.PositiveIntegerField()),
                ("status", models.CharField(choices=[("available", "Available"), ("reserved", "Reserved"), ("sold", "Sold"), ("archived", "Artist Archive")], default="available", max_length=30)),
                ("reserved_at", models.DateTimeField(blank=True, null=True)),
                ("sold_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"verbose_name": "Photograph Edition", "verbose_name_plural": "Photograph Editions", "ordering": ["photograph", "edition_type", "number"]},
        ),
        migrations.AddConstraint(
            model_name="photographedition",
            constraint=models.UniqueConstraint(fields=["photograph", "edition_type", "number"], name="editions_photographedition_unique"),
        ),
    ]
