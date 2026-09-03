from django.db import models
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class PhotoCollection(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    code = models.SlugField(unique=True, max_length=32, blank=True)
    description = models.TextField(blank=True)
    launch_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Photo Collection"
        verbose_name_plural = "Photo Collections"

    def __str__(self):
        return self.title

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("slug"),
                FieldPanel("code"),
            ],
            heading="Collection identity",
        ),
        FieldPanel("description"),
        FieldPanel("launch_date"),
        FieldPanel("is_active"),
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.code:
            self.code = slugify(self.title)[:32]
        super().save(*args, **kwargs)


@register_snippet
class Photograph(models.Model):
    collection = models.ForeignKey(
        PhotoCollection,
        on_delete=models.CASCADE,
        related_name="photographs",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    code = models.SlugField(max_length=32, blank=True)
    location_name = models.CharField(max_length=200, blank=True)
    story = models.TextField(blank=True)
    edition_details_text = models.TextField(blank=True)
    native_ratio = models.CharField(max_length=10, blank=True, help_text="e.g. 3:2 or 4:5")
    image = models.ImageField(upload_to="editions/photographs/", null=True, blank=True)
    hero_image = models.ImageField(upload_to="editions/heroes/", null=True, blank=True)
    public_edition_size = models.PositiveIntegerField(default=5)
    artist_proof_size = models.PositiveIntegerField(default=2)
    available_as_portrait = models.BooleanField(default=True)
    available_as_landscape = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_sold_out = models.BooleanField(default=False)
    is_preorder = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["collection", "slug"], name="editions_photograph_unique_collection_slug")]
        ordering = ["collection__title", "title"]
        verbose_name = "Photograph"
        verbose_name_plural = "Photographs"

    def __str__(self):
        return self.title

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("collection"),
                FieldPanel("title"),
                FieldPanel("slug"),
                FieldPanel("code"),
                FieldPanel("location_name"),
            ],
            heading="Photograph identity",
        ),
        FieldPanel("story"),
        FieldPanel("edition_details_text"),
        FieldPanel("native_ratio"),
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("hero_image"),
            ],
            heading="Images",
        ),
        MultiFieldPanel(
            [
                FieldPanel("public_edition_size"),
                FieldPanel("artist_proof_size"),
                FieldPanel("available_as_portrait"),
                FieldPanel("available_as_landscape"),
                FieldPanel("is_active"),
                FieldPanel("is_sold_out"),
                FieldPanel("is_preorder"),
            ],
            heading="Edition status",
        ),
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.code:
            self.code = slugify(self.title)[:32]
        super().save(*args, **kwargs)

    @property
    def sold_public_editions(self):
        return self.editions.filter(
            edition_type=PhotographEdition.EDITION_PUBLIC,
            status=PhotographEdition.STATUS_SOLD,
        ).count()

    @property
    def remaining_public_editions(self):
        return self.editions.filter(
            edition_type=PhotographEdition.EDITION_PUBLIC,
            status=PhotographEdition.STATUS_AVAILABLE,
        ).count()

    @property
    def availability_label(self):
        remaining = self.remaining_public_editions
        return f"{remaining} of {self.public_edition_size} editions remaining"

    @property
    def formatted_collection_label(self):
        if self.location_name:
            return f"{self.collection.title} · {self.location_name}"
        return self.collection.title

    def sync_sold_out_state(self):
        sold_out = self.remaining_public_editions == 0
        if self.is_sold_out != sold_out:
            self.is_sold_out = sold_out
            self.save(update_fields=["is_sold_out"])


@register_snippet
class PhotographEdition(models.Model):
    EDITION_PUBLIC = "public"
    EDITION_AP = "artist_proof"
    EDITION_TYPE_CHOICES = [
        (EDITION_PUBLIC, "Public Edition"),
        (EDITION_AP, "Artist Proof"),
    ]

    STATUS_AVAILABLE = "available"
    STATUS_RESERVED = "reserved"
    STATUS_SOLD = "sold"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_RESERVED, "Reserved"),
        (STATUS_SOLD, "Sold"),
        (STATUS_ARCHIVED, "Artist Archive"),
    ]

    photograph = models.ForeignKey(
        Photograph,
        on_delete=models.CASCADE,
        related_name="editions",
    )
    edition_type = models.CharField(max_length=30, choices=EDITION_TYPE_CHOICES)
    number = models.PositiveIntegerField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    reserved_at = models.DateTimeField(null=True, blank=True)
    sold_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["photograph", "edition_type", "number"], name="editions_photographedition_unique")]
        ordering = ["photograph", "edition_type", "number"]
        verbose_name = "Photograph Edition"
        verbose_name_plural = "Photograph Editions"

    def __str__(self):
        return f"{self.photograph.title} · {self.edition_display}"

    panels = [
        FieldPanel("photograph"),
        FieldPanel("edition_type"),
        FieldPanel("number"),
        FieldPanel("status"),
        FieldPanel("reserved_at"),
        FieldPanel("sold_at"),
    ]

    @property
    def edition_display(self):
        if self.edition_type == self.EDITION_AP:
            return f"AP {self.number}/{self.photograph.artist_proof_size}"
        return f"{self.number}/{self.photograph.public_edition_size}"


@register_snippet
class EditionFormat(models.Model):
    code = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    short_description = models.CharField(max_length=255, blank=True)
    long_description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Edition Format"
        verbose_name_plural = "Edition Formats"

    def __str__(self):
        return self.name

    panels = [
        FieldPanel("code"),
        FieldPanel("name"),
        FieldPanel("short_description"),
        FieldPanel("long_description"),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
    ]


@register_snippet
class PrintSize(models.Model):
    aspect_ratio = models.CharField(max_length=20)
    width_in = models.DecimalField(max_digits=6, decimal_places=2)
    height_in = models.DecimalField(max_digits=6, decimal_places=2)
    label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["aspect_ratio", "width_in", "height_in"], name="editions_printsize_unique")]
        ordering = ["aspect_ratio", "sort_order", "width_in", "height_in"]
        verbose_name = "Print Size"
        verbose_name_plural = "Print Sizes"

    def __str__(self):
        return self.label

    panels = [
        FieldPanel("aspect_ratio"),
        FieldPanel("width_in"),
        FieldPanel("height_in"),
        FieldPanel("label"),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
    ]
