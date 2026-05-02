from django.db import models

from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


class HomePage(Page):
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
    signature_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    projects_eyebrow = models.CharField(max_length=80, default="Projects")
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
    projects_button_text = models.CharField(max_length=80, default="view projects")
    projects_button_link = models.CharField(max_length=255, blank=True, default="#")
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
                FieldPanel("signature_image"),
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
                FieldPanel("projects_button_link"),
                FieldPanel("project_image_one"),
                FieldPanel("project_image_two"),
                FieldPanel("project_image_three"),
                FieldPanel("project_image_four"),
            ],
            heading="Projects Section",
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


class StandardPage(Page):
    """A flexible content page for general site content."""

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
