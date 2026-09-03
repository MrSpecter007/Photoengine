import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.models import Page, Site, Locale

from editions.models import (
    EditionFormat,
    PhotoCollection,
    Photograph,
    PhotographEdition,
    PrintSize,
)
from home.models import (
    AdminExperienceSettings,
    ContactPage,
    GalleryPage,
    HomePage,
    PortfolioCategoryPage,
    PortfolioIndexPage,
)

User = get_user_model()


COLLECTIONS = [
    {
        "title": "Urban Light",
        "description": "A series exploring the interplay of artificial light and city architecture at dusk and dawn.",
        "launch_date": datetime.date(2024, 3, 1),
        "photographs": [
            {
                "title": "Neon Corridor",
                "location_name": "Montreal, QC",
                "story": (
                    "Shot at 2 a.m. in the heart of downtown Montreal, this image captures the quiet tension "
                    "of an empty alley drenched in competing neon reflections. The rain-slicked pavement "
                    "doubles the geometry above."
                ),
                "edition_details_text": "Fine art giclée print on 310 gsm rag paper. Limited to 5 public editions.",
                "native_ratio": "3:2",
                "public_edition_size": 5,
                "artist_proof_size": 2,
            },
            {
                "title": "Platform Zero",
                "location_name": "Toronto, ON",
                "story": (
                    "The last train of the night. Long-exposure over 8 seconds compressed the few remaining "
                    "commuters into ghostly trails against the brutalist concrete of a downtown metro platform."
                ),
                "edition_details_text": "Fine art giclée print on 310 gsm rag paper. Limited to 5 public editions.",
                "native_ratio": "3:2",
                "public_edition_size": 5,
                "artist_proof_size": 2,
            },
            {
                "title": "Signal Tower",
                "location_name": "Quebec City, QC",
                "story": (
                    "A broadcasting tower rises above old-city rooftops at blue hour. The tower's warning "
                    "lights blink in 4-second intervals — this frame caught the precise moment all three lit "
                    "simultaneously."
                ),
                "edition_details_text": "Fine art giclée print on 310 gsm rag paper. Limited to 7 public editions.",
                "native_ratio": "4:5",
                "public_edition_size": 7,
                "artist_proof_size": 2,
            },
        ],
    },
    {
        "title": "Northern Wilderness",
        "description": "Landscape work documenting the boreal forest and subarctic tundra across northern Quebec and Labrador.",
        "launch_date": datetime.date(2024, 9, 15),
        "photographs": [
            {
                "title": "Taiga Threshold",
                "location_name": "Lac-Saint-Jean, QC",
                "story": (
                    "Standing at the precise edge where the boreal forest gives way to open muskeg, "
                    "this photograph documents a boundary that is moving northward at roughly 30 km per decade."
                ),
                "edition_details_text": "Fine art giclée print on 310 gsm baryta paper. Limited to 5 public editions.",
                "native_ratio": "16:9",
                "public_edition_size": 5,
                "artist_proof_size": 2,
            },
            {
                "title": "Frost Map",
                "location_name": "Labrador, NL",
                "story": (
                    "Ice crystals on a frozen lake surface form fractal patterns that mirror satellite imagery "
                    "of the same region. Shot from directly overhead, face-down on the ice at -28°C."
                ),
                "edition_details_text": "Fine art giclée print on 310 gsm rag paper. Limited to 5 public editions.",
                "native_ratio": "1:1",
                "public_edition_size": 5,
                "artist_proof_size": 2,
            },
            {
                "title": "Understory",
                "location_name": "Abitibi-Témiscamingue, QC",
                "story": (
                    "The forest floor after a three-day rain. Every surface holds water; every surface reflects. "
                    "Made with a tilt-shift lens to isolate the plane of fallen leaves from an overwhelming depth."
                ),
                "edition_details_text": "Fine art giclée print on 310 gsm rag paper. Limited to 5 public editions.",
                "native_ratio": "3:2",
                "public_edition_size": 5,
                "artist_proof_size": 2,
            },
            {
                "title": "Aurora Column",
                "location_name": "Kuujjuaq, QC",
                "story": (
                    "A single vertical aurora formation — unusually narrow and bright — appeared for eleven "
                    "minutes during an otherwise quiet geomagnetic night. This frame is from the fourth minute."
                ),
                "edition_details_text": "Fine art giclée print on 310 gsm baryta paper. Limited to 10 public editions.",
                "native_ratio": "4:5",
                "public_edition_size": 10,
                "artist_proof_size": 2,
            },
        ],
    },
    {
        "title": "Abstract Moments",
        "description": "Motion studies and macro work that strips familiar subjects down to pure form, texture, and light.",
        "launch_date": datetime.date(2025, 1, 20),
        "photographs": [
            {
                "title": "Dissolve",
                "location_name": "Studio",
                "story": (
                    "Ink dropped into water at 1/4000 s. The cloud of pigment expands differently every time; "
                    "no two frames are alike. This particular dispersion was selected from 840 exposures."
                ),
                "edition_details_text": "Fine art giclée print on 310 gsm rag paper. Limited to 5 public editions.",
                "native_ratio": "1:1",
                "public_edition_size": 5,
                "artist_proof_size": 2,
            },
            {
                "title": "Thread Count",
                "location_name": "Studio",
                "story": (
                    "A section of raw linen fabric photographed through a macro lens at f/16. "
                    "What appears abstract at normal scale resolves, on close inspection, into the precise "
                    "geometry of a plain weave — every thread in the frame is in contact with every adjacent thread."
                ),
                "edition_details_text": "Fine art giclée print on 310 gsm rag paper. Limited to 5 public editions.",
                "native_ratio": "3:2",
                "public_edition_size": 5,
                "artist_proof_size": 2,
            },
        ],
    },
]

EDITION_FORMATS = [
    {
        "code": "fine-art-print",
        "name": "Fine Art Print",
        "short_description": "Giclée print on 310 gsm cotton rag paper with archival pigment inks.",
        "long_description": (
            "Produced on a 12-colour wide-format printer using archival pigment inks on acid-free, "
            "310 gsm heavyweight cotton rag paper. Each print is examined under controlled lighting before "
            "dispatch and ships flat in a rigid protective mailer."
        ),
    },
    {
        "code": "baryta-print",
        "name": "Baryta Print",
        "short_description": "High-gloss baryta paper with a traditional darkroom feel.",
        "long_description": (
            "Printed on premium baryta paper — a silver-halide-coated base that delivers exceptional "
            "shadow depth and a luminous highlight range. Preferred by collectors who favour the look of "
            "traditional fibre-based darkroom prints."
        ),
    },
]

PRINT_SIZES = [
    {"aspect_ratio": "3:2", "width_in": "12.00", "height_in": "8.00", "label": '12" × 8"'},
    {"aspect_ratio": "3:2", "width_in": "18.00", "height_in": "12.00", "label": '18" × 12"'},
    {"aspect_ratio": "3:2", "width_in": "24.00", "height_in": "16.00", "label": '24" × 16"'},
    {"aspect_ratio": "3:2", "width_in": "36.00", "height_in": "24.00", "label": '36" × 24"'},
    {"aspect_ratio": "4:5", "width_in": "16.00", "height_in": "20.00", "label": '16" × 20"'},
    {"aspect_ratio": "4:5", "width_in": "20.00", "height_in": "25.00", "label": '20" × 25"'},
    {"aspect_ratio": "1:1", "width_in": "12.00", "height_in": "12.00", "label": '12" × 12"'},
    {"aspect_ratio": "1:1", "width_in": "20.00", "height_in": "20.00", "label": '20" × 20"'},
    {"aspect_ratio": "16:9", "width_in": "32.00", "height_in": "18.00", "label": '32" × 18"'},
]


class Command(BaseCommand):
    help = "Seed demo portfolio content for the Atelier Lumen Nord showroom."

    def handle(self, *args, **options):
        self._create_superuser()
        self._configure_wagtail()
        self._configure_public_pages()
        self._configure_admin_branding()
        self._seed_edition_formats()
        self._seed_print_sizes()
        self._seed_collections()
        self.stdout.write(self.style.SUCCESS("\nPhotoengine showroom seeded successfully."))
        self.stdout.write("  Site  : http://photo.localhost")
        self.stdout.write("  Admin : http://photo.localhost/admin/")
        self.stdout.write("  Login : admin / photo-demo")

    def _create_superuser(self):
        if User.objects.filter(username="admin").exists():
            self.stdout.write("  Superuser already exists, skipping.")
            return
        User.objects.create_superuser(
            username="admin",
            email="admin@photo.localhost",
            password="photo-demo",
        )
        self.stdout.write("  Created superuser admin / photo-demo")

    def _configure_wagtail(self):
        try:
            root = Page.objects.filter(depth=1).first()
            if root is None:
                self.stdout.write("  Wagtail root page not found; skipping site config.")
                return
            site = Site.objects.first()
            if site:
                site.hostname = "photo.localhost"
                site.port = 80
                site.site_name = "Atelier Lumen Nord"
                home_page = HomePage.objects.live().public().first()
                if home_page:
                    site.root_page = home_page
                site.save()
                self.stdout.write("  Updated Wagtail site hostname.")
        except Exception as exc:
            self.stdout.write(f"  Site config skipped: {exc}")

    def _configure_public_pages(self):
        try:
            root = Page.objects.filter(depth=1).first()
            if root is None:
                self.stdout.write("  Public page setup skipped: Wagtail root page not found.")
                return

            home_page = HomePage.objects.first()
            if home_page is None:
                home_page = HomePage(title="Home", slug="home")
                root.add_child(instance=home_page)

            self._update_page(
                home_page,
                title="Home",
                slug="home",
                show_in_menus=True,
                seo_title="Atelier Lumen Nord",
                search_description=(
                    "A fictional Montreal photography studio showroom with portfolio, "
                    "private proofing, and limited-edition print tracking."
                ),
                about_eyebrow="Studio",
                about_heading="Atelier Lumen Nord\nPhotographic stories from Montreal.",
                about_paragraph_one=(
                    "Atelier Lumen Nord is a fictional Montreal photography studio built "
                    "for the Photoengine showroom. The studio creates calm portrait "
                    "sessions, editorial commissions, and image libraries for independent brands."
                ),
                about_paragraph_two=(
                    "The public site, private proofing portal, and limited-edition archive "
                    "share one restrained visual system so clients and collectors always know "
                    "where they are."
                ),
                projects_eyebrow="Portfolio",
                projects_heading="Portraits, commissions,\nand quiet commercial stories",
                projects_paragraph_one=(
                    "Browse selected studio projects spanning editorial portraits, interior "
                    "studies, maker profiles, and atmospheric product work."
                ),
                projects_paragraph_two=(
                    "Each gallery is structured for a real client workflow: a curated public "
                    "portfolio, private proofing access, and clear final delivery."
                ),
                projects_button_text="View portfolio",
                testimonial_quote=(
                    '"The studio made selection easy. Our proofing gallery felt private, '
                    'calm, and organized, and the final images matched the brief exactly."'
                ),
                testimonial_client_name="Elise Marceau",
                testimonial_client_job="Creative Director, Alder & Finch",
                partners_heading="Studio Services",
                partners_intro=(
                    "A compact set of photography services designed for people who need "
                    "images that feel considered, useful, and easy to approve."
                ),
                partner_one_name="Editorial Portraits",
                partner_one_description=(
                    "Natural, composed portraits for founders, artists, and small teams."
                ),
                partner_two_name="Architecture & Interiors",
                partner_two_description=(
                    "Quiet room studies, spatial details, and hospitality environments."
                ),
                partner_three_name="Private Proofing",
                partner_three_description=(
                    "Secure client galleries for reviewing, favoriting, and approving images."
                ),
                partner_four_name="Fine Art Editions",
                partner_four_description=(
                    "Numbered print releases with availability and format details."
                ),
                contact_eyebrow="Inquiries",
                contact_heading="Planning a session?",
                contact_heading_emphasis="Start here.",
                contact_link="/contact/",
            )

            portfolio_page = self._get_or_create_child(
                parent=home_page,
                model=PortfolioIndexPage,
                slug="portfolio",
                title="Portfolio",
            )
            self._update_page(
                portfolio_page,
                title="Portfolio",
                slug="portfolio",
                show_in_menus=True,
                intro=(
                    "Selected fictional projects from Atelier Lumen Nord: editorial portraits, "
                    "interiors, maker stories, and field studies for the showroom."
                ),
            )

            category_specs = [
                (
                    "portrait-commissions",
                    "Portrait Commissions",
                    "Quiet editorial portraits for founders, artists, designers, and small teams.",
                    [
                        (
                            "riverside-portrait-session",
                            "Riverside Portrait Session",
                            "A soft winter-light portrait story for a fictional ceramic artist near the Lachine Canal.",
                        ),
                        (
                            "studio-founder-profiles",
                            "Studio Founder Profiles",
                            "Composed profile images for a small architecture collective launching a new practice.",
                        ),
                    ],
                ),
                (
                    "editorial-commercial",
                    "Editorial & Commercial",
                    "Visual stories for independent brands, hospitality spaces, and creative teams.",
                    [
                        (
                            "workshop-light-study",
                            "Workshop Light Study",
                            "A maker-space image library focused on tools, hands, and clean afternoon light.",
                        ),
                        (
                            "quiet-rooms",
                            "Quiet Rooms",
                            "Interior studies for a fictional boutique hotel with linen, wood, and morning shadows.",
                        ),
                    ],
                ),
                (
                    "fine-art-studies",
                    "Fine Art Studies",
                    "Personal photographic studies that connect the portfolio to the limited-edition releases.",
                    [
                        (
                            "north-shore-field-notes",
                            "North Shore Field Notes",
                            "A restrained landscape sequence built around fog, shorelines, and horizon marks.",
                        ),
                        (
                            "paper-and-light",
                            "Paper and Light",
                            "Small studio abstractions made with folded paper, reflected colour, and long exposures.",
                        ),
                    ],
                ),
            ]

            for category_slug, category_title, category_intro, galleries in category_specs:
                category_page = self._get_or_create_child(
                    parent=portfolio_page,
                    model=PortfolioCategoryPage,
                    slug=category_slug,
                    title=category_title,
                )
                self._update_page(
                    category_page,
                    title=category_title,
                    slug=category_slug,
                    show_in_menus=True,
                    intro=category_intro,
                )

                for gallery_slug, gallery_title, gallery_excerpt in galleries:
                    gallery_page = self._get_or_create_child(
                        parent=category_page,
                        model=GalleryPage,
                        slug=gallery_slug,
                        title=gallery_title,
                    )
                    self._update_page(
                        gallery_page,
                        title=gallery_title,
                        slug=gallery_slug,
                        show_in_menus=True,
                        excerpt=gallery_excerpt,
                        presentation_style=GalleryPage.PRESENTATION_STYLE_DEFAULT,
                    )

            contact_page = self._get_or_create_child(
                parent=home_page,
                model=ContactPage,
                slug="contact",
                title="Contact",
            )
            self._update_page(
                contact_page,
                title="Contact",
                slug="contact",
                show_in_menus=True,
                contact_heading="Plan a session or print inquiry",
                contact_detail_heading="Studio Contact",
                contact_phone="514-555-0187",
                contact_email="hello@lumen-nord.example.com",
                address_heading="Atelier",
                address_text="4020 Rue Saint-Ambroise, Suite 214\nMontreal, QC H4C 2C7",
                form_heading="Tell us about the work",
                form_intro=(
                    "Share a few details and the studio will reply with availability, "
                    "recommended coverage, and next steps."
                ),
                success_message=(
                    "Thanks for reaching out. Your inquiry has been received by the studio."
                ),
            )

            home_page.projects_button_page = portfolio_page
            home_page.contact_link = contact_page.url or "/contact/"
            self._publish_page(home_page)

            site = Site.objects.first()
            if site:
                site.hostname = "photo.localhost"
                site.port = 80
                site.site_name = "Atelier Lumen Nord"
                site.root_page = home_page
                site.save()

            self.stdout.write("  Configured Atelier Lumen Nord public pages.")
        except Exception as exc:
            self.stdout.write(f"  Public page setup skipped: {exc}")

    def _get_or_create_child(self, parent, model, slug, title):
        page = model.objects.child_of(parent).filter(slug=slug).first()
        if page:
            return page

        page = model(title=title, slug=slug)
        parent.add_child(instance=page)
        return page

    def _update_page(self, page, **fields):
        for field, value in fields.items():
            setattr(page, field, value)
        self._publish_page(page)
        return page

    def _publish_page(self, page):
        page.save()
        if not isinstance(page, Page):
            return
        revision = page.save_revision()
        revision.publish()

    def _configure_admin_branding(self):
        try:
            settings_obj = AdminExperienceSettings.objects.first()
            if settings_obj is None:
                settings_obj = AdminExperienceSettings()
            settings_obj.admin_brand_name = "Catalystdev · Photo Studio"
            settings_obj.admin_welcome_title = "Welcome to the studio"
            settings_obj.admin_welcome_message = (
                "Manage your portfolio, limited-edition prints, galleries, and client proofing "
                "sessions — all from one workspace."
            )
            settings_obj.admin_primary_color = "#5B26ED"
            settings_obj.admin_surface_color = "#150021"
            settings_obj.admin_sidebar_color = "#3B0062"
            settings_obj.admin_text_color = "#180024"
            settings_obj.admin_sidebar_text_color = "#F8F7FB"
            settings_obj.admin_sidebar_hover_color = "#4A0A75"
            settings_obj.admin_sidebar_hover_text_color = "#FFFFFF"
            settings_obj.admin_sidebar_selected_color = "#5B26ED"
            settings_obj.admin_sidebar_selected_text_color = "#FFFFFF"
            settings_obj.admin_soft_color = "#EFE6FF"
            settings_obj.save()
            self.stdout.write("  Configured Wagtail admin branding.")
        except Exception as exc:
            self.stdout.write(f"  Admin branding skipped: {exc}")

    def _seed_edition_formats(self):
        for data in EDITION_FORMATS:
            obj, created = EditionFormat.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "short_description": data["short_description"],
                    "long_description": data["long_description"],
                },
            )
            verb = "Created" if created else "Exists"
            self.stdout.write(f"  {verb} format: {obj.name}")

    def _seed_print_sizes(self):
        for idx, data in enumerate(PRINT_SIZES):
            obj, created = PrintSize.objects.update_or_create(
                aspect_ratio=data["aspect_ratio"],
                width_in=data["width_in"],
                height_in=data["height_in"],
                defaults={"label": data["label"], "sort_order": idx},
            )
            if created:
                self.stdout.write(f"  Created size: {obj.label}")

    def _seed_collections(self):
        for coll_data in COLLECTIONS:
            collection, created = PhotoCollection.objects.update_or_create(
                slug=coll_data["title"].lower().replace(" ", "-"),
                defaults={
                    "title": coll_data["title"],
                    "description": coll_data["description"],
                    "launch_date": coll_data["launch_date"],
                    "is_active": True,
                },
            )
            verb = "Created" if created else "Exists"
            self.stdout.write(f"  {verb} collection: {collection.title}")

            for photo_data in coll_data["photographs"]:
                photo_slug = photo_data["title"].lower().replace(" ", "-")
                photograph, p_created = Photograph.objects.update_or_create(
                    collection=collection,
                    slug=photo_slug,
                    defaults={
                        "title": photo_data["title"],
                        "location_name": photo_data["location_name"],
                        "story": photo_data["story"],
                        "edition_details_text": photo_data["edition_details_text"],
                        "native_ratio": photo_data["native_ratio"],
                        "public_edition_size": photo_data["public_edition_size"],
                        "artist_proof_size": photo_data["artist_proof_size"],
                        "is_active": True,
                    },
                )
                if not p_created:
                    self.stdout.write(f"    Updated: {photograph.title}")
                    continue

                self.stdout.write(f"    Created: {photograph.title}")
                self._create_editions(photograph)

    def _create_editions(self, photograph: Photograph):
        for n in range(1, photograph.public_edition_size + 1):
            PhotographEdition.objects.get_or_create(
                photograph=photograph,
                edition_type=PhotographEdition.EDITION_PUBLIC,
                number=n,
                defaults={"status": PhotographEdition.STATUS_AVAILABLE},
            )
        for n in range(1, photograph.artist_proof_size + 1):
            PhotographEdition.objects.get_or_create(
                photograph=photograph,
                edition_type=PhotographEdition.EDITION_AP,
                number=n,
                defaults={"status": PhotographEdition.STATUS_ARCHIVED},
            )

        # Mark first two public editions as sold for realism
        public_editions = PhotographEdition.objects.filter(
            photograph=photograph,
            edition_type=PhotographEdition.EDITION_PUBLIC,
        ).order_by("number")[:2]
        for edition in public_editions:
            edition.status = PhotographEdition.STATUS_SOLD
            edition.sold_at = timezone.now()
            edition.save(update_fields=["status", "sold_at"])
