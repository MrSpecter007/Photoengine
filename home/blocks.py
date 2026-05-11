from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class FullWidthImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)
    overlay_text = blocks.CharBlock(required=False)

    class Meta:
        template = "home/blocks/full_width_image.html"
        icon = "image"
        label = "Full-Width Image"


class FullWidthVideoBlock(blocks.StructBlock):
    video_url = blocks.URLBlock(help_text="YouTube, Vimeo, or direct video URL")
    poster_image = ImageChooserBlock(required=False)
    caption = blocks.CharBlock(required=False)

    class Meta:
        template = "home/blocks/full_width_video.html"
        icon = "media"
        label = "Full-Width Video"


class ImageGalleryBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    images = blocks.ListBlock(ImageChooserBlock())
    columns = blocks.ChoiceBlock(
        choices=[("2", "2 Columns"), ("3", "3 Columns"), ("4", "4 Columns")],
        default="3",
    )

    class Meta:
        template = "home/blocks/image_gallery.html"
        icon = "image"
        label = "Image Gallery"


class ImageSequenceBlock(blocks.StructBlock):
    """Horizontal cinematic strip of images — for visual rhythm and pacing."""
    images = blocks.ListBlock(ImageChooserBlock())
    caption = blocks.CharBlock(required=False)

    class Meta:
        template = "home/blocks/image_sequence.html"
        icon = "image"
        label = "Image Sequence (Horizontal Strip)"


class TextEssayBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    body = blocks.RichTextBlock()
    align = blocks.ChoiceBlock(
        choices=[
            ("left", "Left"),
            ("center", "Center"),
            ("narrow", "Narrow (Centered Column)"),
        ],
        default="narrow",
    )

    class Meta:
        template = "home/blocks/text_essay.html"
        icon = "doc-full"
        label = "Text Essay"


class PullQuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock()
    attribution = blocks.CharBlock(required=False)

    class Meta:
        template = "home/blocks/pull_quote.html"
        icon = "openquote"
        label = "Pull Quote"


class TwoColumnTextImageBlock(blocks.StructBlock):
    text = blocks.RichTextBlock()
    image = ImageChooserBlock()
    image_position = blocks.ChoiceBlock(
        choices=[("right", "Image Right"), ("left", "Image Left")],
        default="right",
    )
    caption = blocks.CharBlock(required=False)

    class Meta:
        template = "home/blocks/two_column_text_image.html"
        icon = "image"
        label = "Two Column: Text + Image"


class ArtifactGridBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    artifacts = blocks.ListBlock(
        blocks.StructBlock([
            ("image", ImageChooserBlock()),
            ("label", blocks.CharBlock()),
            ("caption", blocks.CharBlock(required=False)),
        ])
    )

    class Meta:
        template = "home/blocks/artifact_grid.html"
        icon = "grip"
        label = "Artifact Grid"


class TechnicalNotesBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False, default="Technical Notes")
    notes = blocks.RichTextBlock()

    class Meta:
        template = "home/blocks/technical_notes.html"
        icon = "list-ul"
        label = "Technical Notes"


class InstagramEmbedBlock(blocks.StructBlock):
    instagram_url = blocks.URLBlock(help_text="Full URL to Instagram post")
    caption = blocks.CharBlock(required=False)

    class Meta:
        template = "home/blocks/instagram_embed.html"
        icon = "link"
        label = "Instagram Embed"


class RelatedPlatformBlock(blocks.StructBlock):
    platform = blocks.ChoiceBlock(
        choices=[
            ("chez_specter", "Chez Specter"),
            ("specter_parts", "Specter Parts"),
            ("specter_builds", "Specter Builds"),
        ]
    )
    url = blocks.URLBlock()
    heading = blocks.CharBlock(required=False)
    description = blocks.TextBlock(required=False)
    cta_label = blocks.CharBlock(required=False, default="Explore")

    class Meta:
        template = "home/blocks/related_platform.html"
        icon = "link"
        label = "Related Platform"


class CreditsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False, default="Credits")
    credits = blocks.RichTextBlock()

    class Meta:
        template = "home/blocks/credits.html"
        icon = "user"
        label = "Credits"


class CTASectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock()
    subtext = blocks.TextBlock(required=False)
    cta_label = blocks.CharBlock(default="Explore")
    cta_url = blocks.URLBlock(required=False)
    style = blocks.ChoiceBlock(
        choices=[("dark", "Dark"), ("cream", "Cream"), ("transparent", "Transparent")],
        default="dark",
    )

    class Meta:
        template = "home/blocks/cta_section.html"
        icon = "radio-empty"
        label = "CTA Section"


CINEMATIC_BODY_BLOCKS = [
    ("full_width_image", FullWidthImageBlock()),
    ("full_width_video", FullWidthVideoBlock()),
    ("image_gallery", ImageGalleryBlock()),
    ("image_sequence", ImageSequenceBlock()),
    ("text_essay", TextEssayBlock()),
    ("pull_quote", PullQuoteBlock()),
    ("two_column_text_image", TwoColumnTextImageBlock()),
    ("artifact_grid", ArtifactGridBlock()),
    ("technical_notes", TechnicalNotesBlock()),
    ("instagram_embed", InstagramEmbedBlock()),
    ("related_platform", RelatedPlatformBlock()),
    ("credits", CreditsBlock()),
    ("cta_section", CTASectionBlock()),
]
