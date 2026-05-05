from pathlib import Path

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.core.validators import RegexValidator
from django.shortcuts import render
from django.utils.text import slugify

from wagtail import blocks
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.fields import StreamField
from wagtail.images import get_image_model
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Orderable
from wagtail.models import Page
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

from PhotoEngine.bulk_uploads import MultipleImageFileField, build_bulk_upload_help_text
from PhotoEngine.translation_images import TranslationImageSyncMixin


hex_color_validator = RegexValidator(
    regex=r"^#[0-9A-Fa-f]{6}$",
    message="Enter a valid hex color like #DA0D2B.",
)


class GalleryPageAdminForm(WagtailAdminPageForm):
    bulk_upload_images = MultipleImageFileField(
        required=False,
        help_text=build_bulk_upload_help_text(
            "Upload multiple images and attach them directly to this gallery."
        ),
        dropzone_title="Drag and drop gallery images here",
        dropzone_hint="or click to browse a batch of optimized images",
    )

    def save(self, commit=True):
        page = super().save(commit=commit)
        page._pending_bulk_uploads = self.cleaned_data.get("bulk_upload_images") or []
        page._pending_bulk_upload_user = self.for_user
        return page


@register_setting
class AdminExperienceSettings(BaseGenericSetting):
    admin_brand_name = models.CharField(
        max_length=80,
        default="Naji Photo Studio",
        help_text="Short name used for the Wagtail admin experience.",
    )
    admin_welcome_title = models.CharField(
        max_length=120,
        default="Welcome back to the studio",
        help_text="Headline shown on the admin dashboard.",
    )
    admin_welcome_message = models.TextField(
        default=(
            "Use this workspace to publish galleries, manage inquiries, and keep client "
            "projects moving with confidence."
        ),
        help_text="A short dashboard message to make the admin feel personal and familiar.",
    )
    admin_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional square or compact mark used in the custom admin welcome panel.",
    )
    admin_primary_color = models.CharField(
        max_length=7,
        default="#DA0D2B",
        validators=[hex_color_validator],
        help_text="Primary action color for buttons and highlights.",
    )
    admin_surface_color = models.CharField(
        max_length=7,
        default="#1B1B1B",
        validators=[hex_color_validator],
        help_text="Dark surface color used for the admin chrome.",
    )
    admin_sidebar_color = models.CharField(
        max_length=7,
        default="#241A33",
        validators=[hex_color_validator],
        help_text="Sidebar color used for Wagtail navigation and menu states.",
    )
    admin_text_color = models.CharField(
        max_length=7,
        default="#101418",
        validators=[hex_color_validator],
        help_text="Main text color for custom admin welcome content and dashboard accents.",
    )
    admin_sidebar_text_color = models.CharField(
        max_length=7,
        default="#F8F7FB",
        validators=[hex_color_validator],
        help_text="Text color used for sidebar navigation labels and icons.",
    )
    admin_sidebar_hover_color = models.CharField(
        max_length=7,
        default="#000000",
        validators=[hex_color_validator],
        help_text="Sidebar menu background color on hover.",
    )
    admin_sidebar_hover_text_color = models.CharField(
        max_length=7,
        default="#FFFFFF",
        validators=[hex_color_validator],
        help_text="Sidebar menu text and icon color on hover.",
    )
    admin_sidebar_selected_color = models.CharField(
        max_length=7,
        default="#000000",
        validators=[hex_color_validator],
        help_text="Sidebar menu background color for the selected item.",
    )
    admin_sidebar_selected_text_color = models.CharField(
        max_length=7,
        default="#FFFFFF",
        validators=[hex_color_validator],
        help_text="Sidebar menu text and icon color for the selected item.",
    )
    admin_soft_color = models.CharField(
        max_length=7,
        default="#F6E8EC",
        validators=[hex_color_validator],
        help_text="Soft tint used for cards, focus states, and welcome accents.",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("admin_brand_name"),
                FieldPanel("admin_welcome_title"),
                FieldPanel("admin_welcome_message"),
                FieldPanel("admin_logo"),
            ],
            heading="Branding",
        ),
        MultiFieldPanel(
            [
                FieldPanel("admin_primary_color", widget=forms.TextInput(attrs={"type": "color"})),
                FieldPanel("admin_surface_color", widget=forms.TextInput(attrs={"type": "color"})),
                FieldPanel("admin_sidebar_color", widget=forms.TextInput(attrs={"type": "color"})),
                FieldPanel("admin_text_color", widget=forms.TextInput(attrs={"type": "color"})),
                FieldPanel("admin_sidebar_text_color", widget=forms.TextInput(attrs={"type": "color"})),
                FieldPanel("admin_sidebar_hover_color", widget=forms.TextInput(attrs={"type": "color"})),
                FieldPanel("admin_sidebar_hover_text_color", widget=forms.TextInput(attrs={"type": "color"})),
                FieldPanel("admin_sidebar_selected_color", widget=forms.TextInput(attrs={"type": "color"})),
                FieldPanel("admin_sidebar_selected_text_color", widget=forms.TextInput(attrs={"type": "color"})),
                FieldPanel("admin_soft_color", widget=forms.TextInput(attrs={"type": "color"})),
            ],
            heading="Look & Feel",
            help_text="These color controls are intentionally limited so the admin remains clear and usable.",
        ),
    ]

    class Meta:
        verbose_name = "Admin Experience"


class HomePage(TranslationImageSyncMixin, Page):
    translatable_image_fields = (
        "about_image",
        "project_image_one",
        "project_image_two",
        "project_image_three",
        "project_image_four",
        "testimonial_client_image",
        "partner_one_image",
        "partner_two_image",
        "partner_three_image",
        "partner_four_image",
    )

    about_eyebrow = models.CharField(max_length=80, default="about")
    about_heading = models.TextField(
        default="I'm Michel Groch,\nA Professional Photographer\nLiving In Indonesia."
    )
    about_paragraph_one = models.TextField(
        default=(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
            "tempor incididunt ut labore et dolore magna aliqua."
        )
    )
    about_paragraph_two = models.TextField(
        default=(
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
            "aliquip ex ea commodo consequat duis."
        )
    )
    about_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    projects_eyebrow = models.CharField(max_length=80, default="Portfolio")
    projects_heading = models.TextField(default="A Good Ending Is The Most Important")
    projects_paragraph_one = models.TextField(
        default=(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
            "tempor incididunt ut labore et dolore magna aliqua."
        )
    )
    projects_paragraph_two = models.TextField(
        default=(
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
            "aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit."
        )
    )
    projects_button_text = models.CharField(max_length=80, default="view portfolio")
    projects_button_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Select an existing portfolio page or gallery to open from the homepage button.",
    )
    project_image_one = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    project_image_two = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    project_image_three = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    project_image_four = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    testimonial_quote = models.TextField(
        default=(
            '" I\'m very picky with whom I give my energy to. I prefer to reserve my '
            'time, intensity and spirit exclusively to those who reflect sincerity. "'
        )
    )
    testimonial_client_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    testimonial_client_name = models.CharField(max_length=120, default="Tommy Rivers")
    testimonial_client_job = models.CharField(max_length=120, default="Photographer")

    partners_heading = models.CharField(max_length=80, default="Partner")
    partners_intro = models.TextField(
        default=(
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
            "aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit."
        )
    )
    partner_one_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    partner_one_name = models.CharField(max_length=120, default="Fanter Studio")
    partner_one_description = models.TextField(
        default="Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi"
    )
    partner_two_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    partner_two_name = models.CharField(max_length=120, default="GendatGraphic")
    partner_two_description = models.TextField(
        default="Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi"
    )
    partner_three_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    partner_three_name = models.CharField(max_length=120, default="Motor Heads")
    partner_three_description = models.TextField(
        default="Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi"
    )
    partner_four_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    partner_four_name = models.CharField(max_length=120, default="Panthere")
    partner_four_description = models.TextField(
        default="Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi"
    )

    contact_eyebrow = models.CharField(max_length=120, default="So What's Next?")
    contact_heading = models.CharField(max_length=120, default="Are You Ready?")
    contact_heading_emphasis = models.CharField(max_length=120, default="Let's Work!")
    contact_link = models.CharField(max_length=255, blank=True, default="#")

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("about_eyebrow"),
                FieldPanel("about_heading"),
                FieldPanel("about_paragraph_one"),
                FieldPanel("about_paragraph_two"),
                FieldPanel("about_image"),
            ],
            heading="About Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("projects_eyebrow"),
                FieldPanel("projects_heading"),
                FieldPanel("projects_paragraph_one"),
                FieldPanel("projects_paragraph_two"),
                FieldPanel("projects_button_text"),
                PageChooserPanel(
                    "projects_button_page",
                    page_type=["home.PortfolioIndexPage", "home.GalleryPage"],
                ),
                FieldPanel("project_image_one"),
                FieldPanel("project_image_two"),
                FieldPanel("project_image_three"),
                FieldPanel("project_image_four"),
            ],
            heading="Portfolio Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("testimonial_quote"),
                FieldPanel("testimonial_client_image"),
                FieldPanel("testimonial_client_name"),
                FieldPanel("testimonial_client_job"),
            ],
            heading="Testimonial Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("partners_heading"),
                FieldPanel("partners_intro"),
                FieldPanel("partner_one_image"),
                FieldPanel("partner_one_name"),
                FieldPanel("partner_one_description"),
                FieldPanel("partner_two_image"),
                FieldPanel("partner_two_name"),
                FieldPanel("partner_two_description"),
                FieldPanel("partner_three_image"),
                FieldPanel("partner_three_name"),
                FieldPanel("partner_three_description"),
                FieldPanel("partner_four_image"),
                FieldPanel("partner_four_name"),
                FieldPanel("partner_four_description"),
            ],
            heading="Partners Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_eyebrow"),
                FieldPanel("contact_heading"),
                FieldPanel("contact_heading_emphasis"),
                FieldPanel("contact_link"),
            ],
            heading="Contact Call To Action",
        ),
    ]

    def save(self, *args, **kwargs):
        previous_state = self.capture_translation_image_sync_state()
        skip_sync = getattr(self, "_skip_translation_image_sync", False)
        result = super().save(*args, **kwargs)
        if skip_sync:
            self._skip_translation_image_sync = False
            return result
        self.sync_translated_images(previous_state)
        return result

    @property
    def projects_button_target_url(self):
        if self.projects_button_page_id:
            selected_page = self.projects_button_page.specific
            if selected_page.locale_id != self.locale_id:
                try:
                    selected_page = selected_page.get_translation(self.locale).specific
                except ObjectDoesNotExist:
                    pass
            selected_url = selected_page.url if selected_page.live else None
            if selected_url:
                return selected_url

        return ""


class StandardPage(TranslationImageSyncMixin, Page):
    """A flexible content page for general site content."""

    translatable_image_fields = ("header_image",)

    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(
        [
            (
                "heading",
                blocks.CharBlock(
                    form_classname="title",
                    template="home/blocks/heading.html",
                ),
            ),
            ("paragraph", blocks.RichTextBlock(template="home/blocks/paragraph.html")),
            ("image", ImageChooserBlock(template="home/blocks/image.html")),
            ("html", blocks.RawHTMLBlock(template="home/blocks/html.html")),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("header_image"),
        FieldPanel("body"),
    ]

    def save(self, *args, **kwargs):
        previous_state = self.capture_translation_image_sync_state()
        skip_sync = getattr(self, "_skip_translation_image_sync", False)
        result = super().save(*args, **kwargs)
        if skip_sync:
            self._skip_translation_image_sync = False
            return result
        self.sync_translated_images(previous_state)
        return result


class ContactPage(TranslationImageSyncMixin, Page):
    template = "home/contact_page.html"
    translatable_image_fields = ("contact_image",)

    PHOTOGRAPHY_TYPE_WEDDING = "wedding"
    PHOTOGRAPHY_TYPE_ENGAGEMENT = "engagement"
    PHOTOGRAPHY_TYPE_PORTRAIT = "portrait"
    PHOTOGRAPHY_TYPE_FAMILY = "family"
    PHOTOGRAPHY_TYPE_EVENT = "event"
    PHOTOGRAPHY_TYPE_BRAND = "brand"
    PHOTOGRAPHY_TYPE_OTHER = "other"

    contact_heading = models.CharField(
        max_length=120,
        default="In Case You Need Photos",
    )
    contact_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    contact_detail_heading = models.CharField(
        max_length=120,
        default="Contact Detail",
    )
    contact_phone = models.CharField(
        max_length=50,
        blank=True,
        default="(0) 6452 2711 22",
    )
    contact_email = models.EmailField(
        blank=True,
        default="michelgroch@support.com",
    )
    address_heading = models.CharField(
        max_length=120,
        default="Address",
    )
    address_text = models.TextField(
        blank=True,
        default="Lokgebouw 226 5617AC, Eindhoven\nThe Netherlands",
    )
    form_heading = models.CharField(
        max_length=120,
        default="Tell Me About Your Shoot",
    )
    form_intro = models.TextField(
        blank=True,
        default=(
            "Share a few details and I will get back to you with availability, "
            "pricing, and next steps."
        ),
    )
    success_message = models.CharField(
        max_length=255,
        default="Thanks for reaching out. Your inquiry has been received.",
    )

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("contact_heading"),
                FieldPanel("contact_image"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_detail_heading"),
                FieldPanel("contact_phone"),
                FieldPanel("contact_email"),
                FieldPanel("address_heading"),
                FieldPanel("address_text"),
            ],
            heading="Contact Details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("form_heading"),
                FieldPanel("form_intro"),
                FieldPanel("success_message"),
            ],
            heading="Inquiry Form",
        ),
    ]

    def get_form(self, data=None, language_code=None):
        from home.forms import ContactInquiryForm

        return ContactInquiryForm(data=data, language_code=language_code)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["form"] = kwargs.get(
            "form",
            self.get_form(language_code=getattr(request, "LANGUAGE_CODE", None)),
        )
        context["form_success"] = kwargs.get("form_success", False)
        return context

    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            form = self.get_form(
                data=request.POST,
                language_code=getattr(request, "LANGUAGE_CODE", None),
            )
            if form.is_valid():
                ContactInquiry.objects.create(
                    page=self,
                    **form.cleaned_data,
                )
                return render(
                    request,
                    self.template,
                    self.get_context(
                        request,
                        form=self.get_form(
                            language_code=getattr(request, "LANGUAGE_CODE", None),
                        ),
                        form_success=True,
                    ),
                )

            return render(
                request,
                self.template,
                self.get_context(request, form=form, form_success=False),
            )

        return super().serve(request, *args, **kwargs)

    def save(self, *args, **kwargs):
        previous_state = self.capture_translation_image_sync_state()
        skip_sync = getattr(self, "_skip_translation_image_sync", False)
        result = super().save(*args, **kwargs)
        if skip_sync:
            self._skip_translation_image_sync = False
            return result
        self.sync_translated_images(previous_state)
        return result


class ContactInquiry(models.Model):
    page = models.ForeignKey(
        "home.ContactPage",
        related_name="inquiries",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone_number = models.CharField(max_length=40)
    photography_type = models.CharField(max_length=40)
    desired_start_date = models.DateField()
    desired_end_date = models.DateField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.photography_type}"


class PortfolioIndexPage(Page):
    intro = models.TextField(blank=True)

    parent_page_types = ["home.HomePage"]
    subpage_types = ["home.PortfolioCategoryPage"]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["categories"] = PortfolioCategoryPage.objects.child_of(self).live().public()
        context["galleries"] = (
            GalleryPage.objects.descendant_of(self)
            .live()
            .public()
            .select_related("featured_image")
            .order_by("path")
        )
        return context


class PortfolioCategoryPage(TranslationImageSyncMixin, Page):
    translatable_image_fields = ("cover_image",)
    intro = models.TextField(blank=True)
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    parent_page_types = ["home.PortfolioIndexPage"]
    subpage_types = ["home.GalleryPage"]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("cover_image"),
    ]

    @property
    def inherited_tag_name(self):
        return self.title.strip()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["galleries"] = (
            GalleryPage.objects.child_of(self)
            .live()
            .public()
            .select_related("featured_image")
            .order_by("path")
        )
        return context

    def save(self, *args, **kwargs):
        previous_state = self.capture_translation_image_sync_state()
        skip_sync = getattr(self, "_skip_translation_image_sync", False)
        previous_title = None
        if self.pk:
            previous_title = (
                PortfolioCategoryPage.objects.filter(pk=self.pk)
                .values_list("title", flat=True)
                .first()
            )

        result = super().save(*args, **kwargs)

        if skip_sync:
            self._skip_translation_image_sync = False
        else:
            self.sync_translated_images(previous_state)

        if previous_title != self.title:
            for child_page in self.get_children().specific():
                if isinstance(child_page, GalleryPage):
                    child_page.sync_inherited_category_tag(
                        old_name=previous_title,
                        category_name=self.inherited_tag_name,
                    )

        return result

    def add_child(self, instance=None, **kwargs):
        child = super().add_child(instance=instance, **kwargs)
        child_page = child.specific
        if isinstance(child_page, GalleryPage):
            child_page.sync_inherited_category_tag(category_name=self.inherited_tag_name)
        return child


class GalleryPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "home.GalleryPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class GalleryPage(TranslationImageSyncMixin, Page):
    translatable_image_fields = ("featured_image",)
    translatable_orderable_relations = {
        "gallery_images": {
            "parent_field": "page",
            "copy_fields": ("image", "caption"),
            "follow_fields": ("image",),
            "preserve_fields": ("caption",),
        },
    }

    PRESENTATION_STYLE_DEFAULT = "default"
    PRESENTATION_STYLE_GRID = "grid"
    PRESENTATION_STYLE_MASONRY = "masonry"
    PRESENTATION_STYLE_ANIMATE_SCROLL_1 = "animate-scroll-1"
    PRESENTATION_STYLE_ANIMATE_SCROLL_3 = "animate-scroll-3"
    PRESENTATION_STYLE_GALLERY_CAROUSEL_1 = "gallery-carousel-1"
    PRESENTATION_STYLE_GALLERY_CAROUSEL_2 = "gallery-carousel-2"

    PRESENTATION_STYLE_CHOICES = [
        (PRESENTATION_STYLE_DEFAULT, "Default"),
        (PRESENTATION_STYLE_GRID, "Grid (Standard)"),
        (PRESENTATION_STYLE_MASONRY, "Masonry"),
        (PRESENTATION_STYLE_ANIMATE_SCROLL_1, "Animate Scroll 1"),
        (PRESENTATION_STYLE_ANIMATE_SCROLL_3, "Animate Scroll 3"),
        (PRESENTATION_STYLE_GALLERY_CAROUSEL_1, "Gallery Carousel 1"),
        (PRESENTATION_STYLE_GALLERY_CAROUSEL_2, "Gallery Carousel 2"),
    ]

    excerpt = models.TextField(blank=True)
    presentation_style = models.CharField(
        max_length=32,
        choices=PRESENTATION_STYLE_CHOICES,
        default=PRESENTATION_STYLE_DEFAULT,
    )
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(
        [
            (
                "heading",
                blocks.CharBlock(
                    form_classname="title",
                    template="home/blocks/heading.html",
                ),
            ),
            ("paragraph", blocks.RichTextBlock(template="home/blocks/paragraph.html")),
            ("image", ImageChooserBlock(template="home/blocks/image.html")),
            ("html", blocks.RawHTMLBlock(template="home/blocks/html.html")),
        ],
        use_json_field=True,
        blank=True,
    )
    tags = ClusterTaggableManager(through="home.GalleryPageTag", blank=True)
    base_form_class = GalleryPageAdminForm

    parent_page_types = ["home.PortfolioCategoryPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("excerpt"),
        FieldPanel("presentation_style"),
        FieldPanel("featured_image"),
        FieldPanel("bulk_upload_images"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label="Gallery images"),
        FieldPanel("body"),
    ]

    @property
    def category_page(self):
        parent = self.get_parent()
        if parent:
            parent = parent.specific
            if isinstance(parent, PortfolioCategoryPage):
                return parent
        return None

    @property
    def primary_category_name(self):
        category = self.category_page
        return category.inherited_tag_name if category else ""

    @property
    def card_image(self):
        if self.featured_image:
            return self.featured_image

        first_gallery_image = self.gallery_images.select_related("image").first()
        return first_gallery_image.image if first_gallery_image else None

    def attach_uploaded_images(self, uploaded_files, user=None):
        previous_state = self.capture_translation_image_sync_state(include_relations=True)
        image_model = get_image_model()
        existing_gallery_images = list(self.gallery_images.all())
        sort_base = max(
            (gallery_image.sort_order or 0 for gallery_image in existing_gallery_images),
            default=0,
        )
        first_created_image = None

        for index, uploaded_file in enumerate(uploaded_files, start=1):
            image = image_model(
                title=Path(uploaded_file.name).stem,
                file=uploaded_file,
                uploaded_by_user=user if getattr(user, "is_authenticated", False) else None,
            )
            image.save()

            self.gallery_images.add(
                GalleryPageImage(
                    page=self,
                    image=image,
                    sort_order=sort_base + index,
                )
            )

            if first_created_image is None:
                first_created_image = image

        if first_created_image and not self.featured_image_id:
            self.featured_image = first_created_image
            if self.pk:
                type(self).objects.filter(pk=self.pk).update(featured_image=first_created_image)

        self.sync_translated_images(previous_state, include_relations=True)

    @property
    def body_class(self):
        if self.presentation_style == self.PRESENTATION_STYLE_ANIMATE_SCROLL_3:
            return "animate-scroll-3"
        return ""

    def sync_inherited_category_tag(self, old_name=None, category_name=None):
        if category_name is None:
            category = self.category_page
            if not category:
                return
            category_name = category.inherited_tag_name

        if not category_name:
            return

        category_tag, _ = Tag.objects.get_or_create(
            slug=slugify(category_name),
            defaults={"name": category_name},
        )

        if old_name and old_name != category_name:
            old_slug = slugify(old_name)
            GalleryPageTag.objects.filter(
                content_object=self,
                tag__slug=old_slug,
            ).delete()

        GalleryPageTag.objects.get_or_create(
            content_object=self,
            tag=category_tag,
        )

    def save(self, *args, **kwargs):
        previous_state = self.capture_translation_image_sync_state()
        skip_sync = getattr(self, "_skip_translation_image_sync", False)
        result = super().save(*args, **kwargs)
        if skip_sync:
            self._skip_translation_image_sync = False
        else:
            self.sync_translated_images(previous_state)
        self.sync_inherited_category_tag()
        return result

    def save_revision(self, *args, **kwargs):
        previous_state = self.capture_translation_image_sync_state(include_relations=True)
        pending_uploads = getattr(self, "_pending_bulk_uploads", None) or []
        pending_user = getattr(self, "_pending_bulk_upload_user", None)

        if pending_uploads:
            self.attach_uploaded_images(pending_uploads, user=pending_user)
            self._pending_bulk_uploads = []
            self._pending_bulk_upload_user = None

        result = super().save_revision(*args, **kwargs)
        self.sync_translated_images(previous_state, include_relations=True)
        return result

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        category = self.category_page
        if category:
            context["related_galleries"] = (
                GalleryPage.objects.child_of(category)
                .live()
                .public()
                .exclude(pk=self.pk)
                .select_related("featured_image")
                .order_by("path")
            )
        else:
            context["related_galleries"] = GalleryPage.objects.none()
        return context


class GalleryPageImage(Orderable):
    page = ParentalKey(
        "home.GalleryPage",
        related_name="gallery_images",
        on_delete=models.CASCADE,
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
    )
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]
