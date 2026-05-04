import tempfile
import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import Client, TestCase, override_settings
from django.utils.translation import override
from wagtail.images import get_image_model

from home.models import (
    AdminExperienceSettings,
    ContactInquiry,
    ContactPage,
    GalleryPage,
    HomePage,
    PortfolioCategoryPage,
    PortfolioIndexPage,
)

from wagtail.models import Page
from wagtail.models import Locale
from wagtail.test.utils import WagtailPageTestCase

from home.wagtail_hooks import render_admin_experience_css, render_admin_experience_js

GIF_BYTES = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00"
    b"\x00\x00\x00\xff\xff\xff!\xf9\x04"
    b"\x01\x00\x00\x00\x00,\x00\x00\x00"
    b"\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class HomeSetUpTests(WagtailPageTestCase):
    """
    Tests for basic page structure setup and HomePage creation.
    """

    def test_root_create(self):
        root_page = Page.objects.get(pk=1)
        self.assertIsNotNone(root_page)

    def test_homepage_create(self):
        root_page = Page.objects.get(pk=1)
        homepage = HomePage(title="Home Secondary", slug="home-secondary")
        root_page.add_child(instance=homepage)
        self.assertTrue(HomePage.objects.filter(title="Home Secondary").exists())


class AdminExperienceSettingsTests(TestCase):
    def test_admin_experience_settings_load_defaults(self):
        settings_obj = AdminExperienceSettings.load()

        self.assertEqual(settings_obj.admin_brand_name, "Naji Photo Studio")
        self.assertEqual(settings_obj.admin_primary_color, "#DA0D2B")
        self.assertEqual(settings_obj.admin_sidebar_color, "#241A33")
        self.assertEqual(settings_obj.admin_text_color, "#101418")
        self.assertEqual(settings_obj.admin_sidebar_text_color, "#F8F7FB")
        self.assertEqual(settings_obj.admin_sidebar_hover_color, "#000000")
        self.assertEqual(settings_obj.admin_sidebar_hover_text_color, "#FFFFFF")
        self.assertEqual(settings_obj.admin_sidebar_selected_color, "#000000")
        self.assertEqual(settings_obj.admin_sidebar_selected_text_color, "#FFFFFF")

    def test_admin_experience_assets_reflect_saved_settings(self):
        settings_obj = AdminExperienceSettings.load()
        settings_obj.admin_brand_name = "Studio Console"
        settings_obj.admin_primary_color = "#123456"
        settings_obj.admin_surface_color = "#222222"
        settings_obj.admin_sidebar_color = "#345678"
        settings_obj.admin_text_color = "#111111"
        settings_obj.admin_sidebar_text_color = "#FAFAFA"
        settings_obj.admin_sidebar_hover_color = "#010101"
        settings_obj.admin_sidebar_hover_text_color = "#FEFEFE"
        settings_obj.admin_sidebar_selected_color = "#020202"
        settings_obj.admin_sidebar_selected_text_color = "#FDFDFD"
        settings_obj.admin_soft_color = "#EFE8E1"
        settings_obj.save()

        css = render_admin_experience_css()
        js = render_admin_experience_js()

        self.assertIn("#123456", css)
        self.assertIn("#222222", css)
        self.assertIn("#345678", css)
        self.assertIn("#111111", css)
        self.assertIn("#FAFAFA", css)
        self.assertIn("#010101", css)
        self.assertIn("#FEFEFE", css)
        self.assertIn("#020202", css)
        self.assertIn("#FDFDFD", css)
        self.assertIn("Studio Console", js)

    def test_admin_experience_css_supports_sidebar_state_colors(self):
        settings_obj = AdminExperienceSettings.load()
        settings_obj.admin_sidebar_color = "#FFFFFF"
        settings_obj.admin_sidebar_text_color = "#000000"
        settings_obj.admin_sidebar_hover_color = "#000000"
        settings_obj.admin_sidebar_hover_text_color = "#FFFFFF"
        settings_obj.admin_sidebar_selected_color = "#000000"
        settings_obj.admin_sidebar_selected_text_color = "#FFFFFF"
        settings_obj.save()

        css = render_admin_experience_css()

        self.assertIn("#FFFFFF", css)
        self.assertIn("#000000", css)


class HomeTests(WagtailPageTestCase):
    """
    Tests for homepage functionality and rendering.
    """

    def setUp(self):
        """
        Use the Wagtail-served homepage created by migrations.
        """
        self.homepage = HomePage.objects.first()
        if self.homepage is None:
            root_page = Page.objects.get(pk=1)
            self.homepage = HomePage(title="Home", slug="home")
            root_page.add_child(instance=self.homepage)

    def test_homepage_status_code(self):
        response = self.client.get(self.homepage.url)
        self.assertEqual(response.status_code, 200)

    def test_homepage_template_used(self):
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "home/home_page.html")


class NavigationTests(WagtailPageTestCase):
    def setUp(self):
        self.root_page = Page.objects.get(pk=1)
        self.homepage = HomePage.objects.first()
        if self.homepage is None:
            self.homepage = HomePage(title="Home", slug="home")
            self.root_page.add_child(instance=self.homepage)

        self.portfolio_index = PortfolioIndexPage(title="Portfolio", slug="portfolio")
        self.homepage.add_child(instance=self.portfolio_index)

        self.category_page = PortfolioCategoryPage(title="Weddings", slug="weddings")
        self.portfolio_index.add_child(instance=self.category_page)

        self.contact_page = ContactPage(title="Contact", slug="contact")
        self.homepage.add_child(instance=self.contact_page)

    def test_navigation_uses_site_pages_and_branding(self):
        response = self.client.get(self.homepage.url)

        self.assertContains(response, "NAJI PHOTO")
        self.assertContains(response, 'href="%s"' % self.portfolio_index.url)
        self.assertContains(response, 'href="%s"' % self.category_page.url)
        self.assertContains(response, 'href="%s"' % reverse("privacy_policy"))
        self.assertContains(response, 'href="%s"' % reverse("proofing:portal"))
        self.assertContains(response, 'href="%s"' % reverse("proofing:legal"))
        self.assertContains(response, 'href="%s"' % self.contact_page.url)
        self.assertContains(response, "Portfolio")


class LocalizationTests(WagtailPageTestCase):
    def setUp(self):
        self.english_home = HomePage.objects.filter(locale__language_code="en").first()
        self.french_locale = Locale.objects.get(language_code="fr")
        self.french_home = self.english_home.get_translation(self.french_locale)

    def test_french_homepage_serves_from_fr_prefix(self):
        response = self.client.get("/fr/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"].pk, self.french_home.pk)

    def test_homepage_language_switcher_links_to_french_translation(self):
        response = self.client.get(self.english_home.url)

        self.assertContains(response, 'hreflang="fr"')
        self.assertContains(response, 'href="%s"' % self.french_home.url)

    def test_french_proofing_portal_route_is_available(self):
        with override("fr"):
            response = self.client.get(reverse("proofing:portal"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Portail d")


class PortfolioPageTests(WagtailPageTestCase):
    def setUp(self):
        self.root_page = Page.objects.get(pk=1)
        self.homepage = HomePage.objects.first()
        if self.homepage is None:
            self.homepage = HomePage(title="Home", slug="home")
            self.root_page.add_child(instance=self.homepage)

        self.portfolio_index = PortfolioIndexPage(title="Portfolio", slug="portfolio")
        self.homepage.add_child(instance=self.portfolio_index)

        self.category_page = PortfolioCategoryPage(title="Weddings", slug="weddings")
        self.portfolio_index.add_child(instance=self.category_page)

    def test_portfolio_index_template_used(self):
        response = self.client.get(self.portfolio_index.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/portfolio_index_page.html")

    def test_gallery_page_inherits_parent_category_tag(self):
        gallery_page = GalleryPage(title="Maya and Noah", slug="maya-and-noah")
        self.category_page.add_child(instance=gallery_page)
        gallery_page.refresh_from_db()

        self.assertTrue(gallery_page.tags.filter(name="Weddings").exists())
        self.assertEqual(
            gallery_page.presentation_style,
            GalleryPage.PRESENTATION_STYLE_DEFAULT,
        )

    def test_category_rename_updates_child_gallery_tag(self):
        gallery_page = GalleryPage(title="Maya and Noah", slug="maya-and-noah")
        self.category_page.add_child(instance=gallery_page)

        self.category_page.title = "Elopements"
        self.category_page.save()
        gallery_page = GalleryPage.objects.get(pk=gallery_page.pk)

        self.assertTrue(gallery_page.tags.filter(name="Elopements").exists())
        self.assertFalse(gallery_page.tags.filter(name="Weddings").exists())

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_gallery_page_bulk_upload_attaches_images(self):
        gallery_page = GalleryPage(title="Maya and Noah", slug="maya-and-noah")
        self.category_page.add_child(instance=gallery_page)

        first_upload = SimpleUploadedFile(
            "first.gif",
            (
                b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
                b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
                b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
            ),
            content_type="image/gif",
        )
        second_upload = SimpleUploadedFile(
            "second.gif",
            (
                b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
                b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
                b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
            ),
            content_type="image/gif",
        )

        gallery_page.attach_uploaded_images([first_upload, second_upload])
        gallery_page.refresh_from_db()

        self.assertEqual(gallery_page.gallery_images.count(), 2)
        self.assertIsNotNone(gallery_page.featured_image)
        self.assertEqual(gallery_page.featured_image.title, "first")

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_gallery_page_revision_processes_pending_bulk_uploads(self):
        gallery_page = GalleryPage(title="Maya and Noah", slug="maya-and-noah")
        self.category_page.add_child(instance=gallery_page)

        gallery_page._pending_bulk_uploads = [
            SimpleUploadedFile(
                "queued.gif",
                (
                    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
                    b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
                    b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
                ),
                content_type="image/gif",
            )
        ]
        gallery_page._pending_bulk_upload_user = None

        gallery_page.save_revision()
        gallery_page.refresh_from_db()

        self.assertEqual(gallery_page.gallery_images.count(), 1)
        self.assertEqual(gallery_page.gallery_images.first().image.title, "queued")

    def test_animate_scroll_three_sets_body_class(self):
        gallery_page = GalleryPage(
            title="Styled Gallery",
            slug="styled-gallery",
            presentation_style=GalleryPage.PRESENTATION_STYLE_ANIMATE_SCROLL_3,
        )
        self.category_page.add_child(instance=gallery_page)

        self.assertEqual(gallery_page.body_class, "animate-scroll-3")


class ImageChooserUploadTests(WagtailPageTestCase):
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_blank_title_upload_uses_filename_in_chooser(self):
        user_model = get_user_model()
        user = user_model.objects.create_superuser(
            username="image-admin",
            email="image-admin@example.com",
            password="pass1234",
        )
        client = Client()
        client.force_login(user)

        image_model = get_image_model()
        before_count = image_model.objects.count()

        response = client.post(
            "/admin/images/chooser/create/",
            {
                "image-chooser-upload-title": "",
                "image-chooser-upload-file": SimpleUploadedFile(
                    "chooser-smoke.gif",
                    (
                        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
                        b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
                        b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
                    ),
                    content_type="image/gif",
                ),
            },
        )

        payload = json.loads(response.content)
        created_image = image_model.objects.order_by("-id").first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(image_model.objects.count(), before_count + 1)
        self.assertEqual(payload["step"], "chosen")
        self.assertEqual(payload["result"]["id"], str(created_image.id))
        self.assertEqual(payload["result"]["title"], "chooser-smoke")
        self.assertEqual(payload["result"]["default_alt_text"], "chooser-smoke")


class ContactPageTests(WagtailPageTestCase):
    def setUp(self):
        self.root_page = Page.objects.get(pk=1)
        self.homepage = HomePage.objects.first()
        if self.homepage is None:
            self.homepage = HomePage(title="Home", slug="home")
            self.root_page.add_child(instance=self.homepage)

        self.contact_page = ContactPage(title="Contact", slug="contact")
        self.homepage.add_child(instance=self.contact_page)

    def test_contact_page_template_used(self):
        response = self.client.get(self.contact_page.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/contact_page.html")

    def test_contact_page_includes_privacy_notice(self):
        response = self.client.get(self.contact_page.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Privacy Policy")
        self.assertContains(response, "By submitting this form")

    def test_contact_page_submission_creates_inquiry(self):
        response = self.client.post(
            self.contact_page.url,
            {
                "name": "Alex Example",
                "email": "alex@example.com",
                "phone_number": "555-111-2222",
                "photography_type": ContactPage.PHOTOGRAPHY_TYPE_BRAND,
                "desired_start_date": "2026-06-10",
                "desired_end_date": "2026-06-12",
                "message": "Looking for a two-day brand session.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ContactInquiry.objects.filter(
                page=self.contact_page,
                email="alex@example.com",
            ).exists()
        )
        self.assertContains(response, self.contact_page.success_message)


class PrivacyPolicyTests(WagtailPageTestCase):
    def setUp(self):
        self.root_page = Page.objects.get(pk=1)
        self.homepage = HomePage.objects.first()
        if self.homepage is None:
            self.homepage = HomePage(title="Home", slug="home")
            self.root_page.add_child(instance=self.homepage)

        self.contact_page = ContactPage(
            title="Contact",
            slug="contact",
            contact_email="privacy@example.com",
            contact_phone="555-111-2222",
        )
        self.homepage.add_child(instance=self.contact_page)

    def test_privacy_policy_page_renders(self):
        response = self.client.get(reverse("privacy_policy"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Privacy Policy")
        self.assertContains(response, "Who this policy applies to")
        self.assertContains(response, "privacy@example.com")

    def test_french_privacy_policy_route_renders_french_copy(self):
        with override("fr"):
            response = self.client.get(reverse("privacy_policy"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Politique de confidentialite")
        self.assertContains(response, "Portee de la politique")


class TranslationImageSyncTests(WagtailPageTestCase):
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_contact_image_syncs_from_english_to_french(self):
        root_page = Page.objects.get(pk=1)
        homepage = HomePage.objects.filter(locale__language_code="en").first()
        if homepage is None:
            homepage = HomePage(title="Home", slug="home")
            root_page.add_child(instance=homepage)

        contact_page = ContactPage(title="Contact Sync", slug="contact-sync")
        homepage.add_child(instance=contact_page)

        french_locale = Locale.objects.get(language_code="fr")
        french_contact = contact_page.copy_for_translation(french_locale, copy_parents=True)
        french_contact.save_revision().publish()

        image_model = get_image_model()
        english_image = image_model.objects.create(
            title="English Contact",
            file=SimpleUploadedFile("english-contact.gif", GIF_BYTES, content_type="image/gif"),
        )

        contact_page.contact_image = english_image
        contact_page.save()
        french_contact.refresh_from_db()

        self.assertEqual(french_contact.contact_image_id, english_image.id)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_manual_french_contact_image_override_stops_future_sync(self):
        root_page = Page.objects.get(pk=1)
        homepage = HomePage.objects.filter(locale__language_code="en").first()
        if homepage is None:
            homepage = HomePage(title="Home", slug="home")
            root_page.add_child(instance=homepage)

        contact_page = ContactPage(title="Contact Override", slug="contact-override")
        homepage.add_child(instance=contact_page)

        french_locale = Locale.objects.get(language_code="fr")
        french_contact = contact_page.copy_for_translation(french_locale, copy_parents=True)
        french_contact.save_revision().publish()

        image_model = get_image_model()
        shared_image = image_model.objects.create(
            title="Shared Contact",
            file=SimpleUploadedFile("shared-contact.gif", GIF_BYTES, content_type="image/gif"),
        )
        override_image = image_model.objects.create(
            title="French Override",
            file=SimpleUploadedFile("french-override.gif", GIF_BYTES, content_type="image/gif"),
        )
        updated_english_image = image_model.objects.create(
            title="Updated English Contact",
            file=SimpleUploadedFile("updated-contact.gif", GIF_BYTES, content_type="image/gif"),
        )

        contact_page.contact_image = shared_image
        contact_page.save()
        french_contact.refresh_from_db()

        french_contact.contact_image = override_image
        french_contact.save()

        contact_page.contact_image = updated_english_image
        contact_page.save()
        french_contact.refresh_from_db()

        self.assertEqual(french_contact.contact_image_id, override_image.id)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_gallery_images_sync_from_english_to_french(self):
        root_page = Page.objects.get(pk=1)
        homepage = HomePage.objects.filter(locale__language_code="en").first()
        if homepage is None:
            homepage = HomePage(title="Home", slug="home")
            root_page.add_child(instance=homepage)

        portfolio_index = PortfolioIndexPage(title="Portfolio Sync", slug="portfolio-sync")
        homepage.add_child(instance=portfolio_index)
        category_page = PortfolioCategoryPage(title="Weddings Sync", slug="weddings-sync")
        portfolio_index.add_child(instance=category_page)
        gallery_page = GalleryPage(title="Gallery Sync", slug="gallery-sync")
        category_page.add_child(instance=gallery_page)

        french_locale = Locale.objects.get(language_code="fr")
        french_gallery = gallery_page.copy_for_translation(french_locale, copy_parents=True)
        french_gallery.save_revision().publish()

        gallery_page.attach_uploaded_images(
            [
                SimpleUploadedFile("gallery-one.gif", GIF_BYTES, content_type="image/gif"),
                SimpleUploadedFile("gallery-two.gif", GIF_BYTES, content_type="image/gif"),
            ]
        )
        french_gallery.refresh_from_db()

        self.assertEqual(french_gallery.gallery_images.count(), 2)
        self.assertEqual(
            list(french_gallery.gallery_images.values_list("image__title", flat=True)),
            ["gallery-one", "gallery-two"],
        )
