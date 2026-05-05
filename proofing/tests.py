from datetime import date
import json
import tempfile
from datetime import timedelta
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import override

from PhotoEngine.bulk_uploads import MultipleImageFileField
from home.models import HomePage
from proofing.models import Client, ClientProofingGallery, ProofImage
from wagtail.models import Locale, Page


GIF_BYTES = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00"
    b"\x00\x00\x00\xff\xff\xff!\xf9\x04"
    b"\x01\x00\x00\x00\x00,\x00\x00\x00"
    b"\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class ProofingMultipleImageFileFieldTests(TestCase):
    def test_rejects_single_image_that_exceeds_per_file_limit(self):
        field = MultipleImageFileField(max_files=5, max_file_bytes=20, max_total_bytes=1024)

        oversized_upload = [
            SimpleUploadedFile("oversized.gif", GIF_BYTES, content_type="image/gif")
        ]

        with self.assertRaises(ValidationError):
            field.clean(oversized_upload)


class ClientProofingGalleryAccessTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.home_page = HomePage.objects.first()
        if self.home_page is None:
            root_page = Page.get_first_root_node()
            self.home_page = HomePage(title="Home", slug="home")
            root_page.add_child(instance=self.home_page)

        self.client_record = Client.objects.create(
            full_name="A Client",
            email="client@example.com",
        )
        self.gallery = ClientProofingGallery(
            title="Client Gallery",
            slug="client-gallery",
            client=self.client_record,
            shoot_date=date(2026, 5, 2),
        )
        self.home_page.add_child(instance=self.gallery)
        self.french_locale = Locale.objects.get_or_create(language_code="fr")[0]

    def test_gallery_requires_token_without_session(self):
        request = self.factory.get("/client-gallery/")
        request.session = {}

        with self.assertRaises(Http404):
            self.gallery.serve(request)

    def test_gallery_grants_session_access_after_valid_token(self):
        request = self.factory.get(f"/client-gallery/?token={self.gallery.access_token}")
        request.session = {}

        response = self.gallery.serve(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            request.session[self.gallery.get_session_access_key()],
            str(self.gallery.access_token),
        )

    def test_gallery_defaults_from_client_record(self):
        self.gallery.refresh_from_db()

        self.assertEqual(self.gallery.client_display_name, "A Client")
        self.assertEqual(self.gallery.client_name, "A Client")
        self.assertEqual(self.gallery.invite_email, "client@example.com")

    def test_gallery_client_name_resyncs_from_client_record(self):
        self.client_record.full_name = "Updated Client"
        self.client_record.save()
        self.gallery.client_name = "Outdated Name"
        self.gallery.save()
        self.gallery.refresh_from_db()

        self.assertEqual(self.gallery.client_name, "Updated Client")
        self.assertEqual(self.gallery.client_display_name, "Updated Client")

    def test_gallery_defaults_to_default_presentation_style(self):
        self.gallery.refresh_from_db()

        self.assertEqual(
            self.gallery.presentation_style,
            ClientProofingGallery.PRESENTATION_STYLE_DEFAULT,
        )
        self.assertTrue(self.gallery.uses_progressive_loading)

    def test_body_class_is_set_for_animate_scroll_three(self):
        self.gallery.presentation_style = (
            ClientProofingGallery.PRESENTATION_STYLE_ANIMATE_SCROLL_3
        )

        self.assertEqual(self.gallery.body_class, "animate-scroll-3")

    def test_proofing_portal_renders(self):
        response = self.client.get(reverse("proofing:portal"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Proofing Portal")
        self.assertContains(response, "Open gallery")

    def test_proofing_legal_page_renders(self):
        response = self.client.get(reverse("proofing:legal"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Proofing Portal Legal Information")
        self.assertContains(response, "Authorized access")

    def test_french_proofing_legal_page_renders_french_copy(self):
        with override("fr"):
            response = self.client.get(reverse("proofing:legal"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Informations legales du portail client")
        self.assertContains(response, "Acces autorise")

    def test_proofing_portal_redirects_with_valid_token(self):
        response = self.client.post(
            reverse("proofing:portal"),
            {"access_token": str(self.gallery.access_token)},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.gallery.url, response["Location"])
        self.assertIn(str(self.gallery.access_token), response["Location"])

    def test_proofing_portal_rejects_unknown_token(self):
        response = self.client.post(
            reverse("proofing:portal"),
            {"access_token": str(uuid4())},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "We couldn&#x27;t find a proofing gallery for that token.",
        )

    def test_french_portal_redirects_to_french_gallery_translation(self):
        french_gallery = self.gallery.copy_for_translation(self.french_locale, copy_parents=True)
        french_gallery.save_revision().publish()

        with override("fr"):
            response = self.client.post(
                reverse("proofing:portal"),
                {"access_token": str(self.gallery.access_token)},
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn(french_gallery.url, response["Location"])


class ProofSelectionViewTests(TestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        if self.home_page is None:
            root_page = Page.get_first_root_node()
            self.home_page = HomePage(title="Home", slug="home")
            root_page.add_child(instance=self.home_page)

        self.client_record = Client.objects.create(full_name="A Client")
        self.gallery = ClientProofingGallery(
            title="Client Gallery",
            slug="client-gallery",
            client=self.client_record,
            shoot_date=date(2026, 5, 2),
        )
        self.home_page.add_child(instance=self.gallery)
        self.french_locale = Locale.objects.get_or_create(language_code="fr")[0]

        from wagtail.images import get_image_model

        image_model = get_image_model()
        self.image = image_model.objects.create(
            title="Proof Image",
            file=SimpleUploadedFile("test.gif", GIF_BYTES, content_type="image/gif"),
        )
        self.proof = ProofImage.objects.create(gallery=self.gallery, image=self.image)

    def create_french_gallery_translation(self):
        french_gallery = self.gallery.copy_for_translation(
            self.french_locale,
            copy_parents=True,
        )
        french_gallery.save_revision().publish()
        return french_gallery

    def create_proofs(self, count):
        from wagtail.images import get_image_model

        image_model = get_image_model()
        created = []

        for index in range(count):
            image = image_model.objects.create(
                title=f"Proof Image {index}",
                file=SimpleUploadedFile(
                    f"test-{index}.gif",
                    GIF_BYTES,
                    content_type="image/gif",
                ),
            )
            created.append(ProofImage.objects.create(gallery=self.gallery, image=image))

        return created

    def test_toggle_requires_access(self):
        response = self.client.post(
            reverse("proofing:toggle_selection"),
            data=json.dumps({"proof_uuid": str(self.proof.proof_uuid)}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_toggle_updates_when_session_is_authorized(self):
        session = self.client.session
        session[self.gallery.get_session_access_key()] = str(self.gallery.access_token)
        session.save()

        response = self.client.post(
            reverse("proofing:toggle_selection"),
            data=json.dumps({"proof_uuid": str(self.proof.proof_uuid)}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.proof.refresh_from_db()
        self.assertTrue(self.proof.selected_by_client)

    def test_translated_gallery_copy_gets_distinct_proof_uuids(self):
        french_gallery = self.create_french_gallery_translation()
        french_proof = french_gallery.proof_images.get(image=self.image)

        self.assertNotEqual(french_proof.proof_uuid, self.proof.proof_uuid)
        self.assertEqual(french_gallery.access_token, self.gallery.access_token)

    def test_toggle_syncs_selection_across_gallery_translations(self):
        french_gallery = self.create_french_gallery_translation()

        session = self.client.session
        session[self.gallery.get_session_access_key()] = str(self.gallery.access_token)
        session.save()

        response = self.client.post(
            reverse("proofing:toggle_selection"),
            data=json.dumps({"proof_uuid": str(self.proof.proof_uuid)}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        french_proof = french_gallery.proof_images.get(image=self.image)
        self.assertTrue(french_proof.selected_by_client)

    def test_finalize_requires_a_selection(self):
        session = self.client.session
        session[self.gallery.get_session_access_key()] = str(self.gallery.access_token)
        session.save()

        response = self.client.post(
            reverse("proofing:finalize_selection"),
            data=json.dumps({"gallery_id": self.gallery.pk}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.gallery.refresh_from_db()
        self.assertFalse(self.gallery.is_locked)

    def test_finalize_locks_gallery_when_session_is_authorized(self):
        self.proof.selected_by_client = True
        self.proof.save(update_fields=["selected_by_client"])
        french_gallery = self.create_french_gallery_translation()
        french_gallery.proof_images.filter(image=self.image).update(selected_by_client=True)

        session = self.client.session
        session[self.gallery.get_session_access_key()] = str(self.gallery.access_token)
        session.save()

        response = self.client.post(
            reverse("proofing:finalize_selection"),
            data=json.dumps({"gallery_id": self.gallery.pk}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.gallery.refresh_from_db()
        french_gallery.refresh_from_db()
        self.assertTrue(self.gallery.is_locked)
        self.assertTrue(french_gallery.is_locked)
        self.assertEqual(self.gallery.session_status, ClientProofingGallery.STATUS_FINALIZED)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_bulk_upload_attaches_proof_images(self):
        initial_count = self.gallery.proof_images.count()
        self.gallery.attach_uploaded_images(
            [
                SimpleUploadedFile("proof-one.gif", GIF_BYTES, content_type="image/gif"),
                SimpleUploadedFile("proof-two.gif", GIF_BYTES, content_type="image/gif"),
            ]
        )
        self.gallery.refresh_from_db()

        self.assertEqual(self.gallery.proof_images.count(), initial_count + 2)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_bulk_upload_syncs_proof_images_to_french_translation(self):
        french_gallery = self.create_french_gallery_translation()

        self.gallery.attach_uploaded_images(
            [
                SimpleUploadedFile("proof-one.gif", GIF_BYTES, content_type="image/gif"),
                SimpleUploadedFile("proof-two.gif", GIF_BYTES, content_type="image/gif"),
            ]
        )
        french_gallery.refresh_from_db()

        self.assertEqual(french_gallery.proof_images.count(), self.gallery.proof_images.count())
        self.assertEqual(
            list(french_gallery.proof_images.values_list("image__title", flat=True)),
            list(self.gallery.proof_images.values_list("image__title", flat=True)),
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_revision_processes_pending_bulk_uploads(self):
        initial_count = self.gallery.proof_images.count()
        self.gallery._pending_bulk_uploads = [
            SimpleUploadedFile("queued-proof.gif", GIF_BYTES, content_type="image/gif")
        ]
        self.gallery._pending_bulk_upload_user = None

        self.gallery.save_revision()
        self.gallery.refresh_from_db()

        self.assertEqual(self.gallery.proof_images.count(), initial_count + 1)
        self.assertTrue(
            self.gallery.proof_images.filter(image__title="queued-proof").exists()
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_gallery_context_limits_initial_proof_batch(self):
        self.create_proofs(30)

        request = RequestFactory().get(self.gallery.url)
        request.session = {
            self.gallery.get_session_access_key(): str(self.gallery.access_token)
        }

        context = self.gallery.get_context(request)

        self.assertEqual(len(context["proof_images"]), self.gallery.proofs_per_page)
        self.assertTrue(context["proof_page"].has_next())

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_load_more_proofs_requires_access(self):
        self.create_proofs(5)

        response = self.client.get(
            reverse("proofing:load_more_proofs"),
            {"gallery_id": self.gallery.pk, "page": 1},
        )

        self.assertEqual(response.status_code, 403)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_load_more_proofs_returns_paginated_html(self):
        self.create_proofs(30)

        session = self.client.session
        session[self.gallery.get_session_access_key()] = str(self.gallery.access_token)
        session.save()

        response = self.client.get(
            reverse("proofing:load_more_proofs"),
            {"gallery_id": self.gallery.pk, "page": 2},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "success")
        self.assertIn("Proof Image 28", payload["html"])
        self.assertFalse(payload["has_next"])
        self.assertIsNone(payload["next_page"])

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_non_progressive_style_renders_full_gallery_in_initial_context(self):
        self.gallery.presentation_style = (
            ClientProofingGallery.PRESENTATION_STYLE_GALLERY_CAROUSEL_1
        )
        self.gallery.save(update_fields=["presentation_style"])
        self.create_proofs(30)

        request = RequestFactory().get(self.gallery.url)
        request.session = {
            self.gallery.get_session_access_key(): str(self.gallery.access_token)
        }

        context = self.gallery.get_context(request)

        self.assertFalse(context["uses_progressive_loading"])
        self.assertEqual(len(context["proof_images"]), self.gallery.proof_images.count())

    def test_gallery_page_displays_proof_image_title(self):
        session = self.client.session
        session[self.gallery.get_session_access_key()] = str(self.gallery.access_token)
        session.save()

        response = self.client.get(self.gallery.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Image Proof Image")
        self.assertContains(response, "Client portal")
        self.assertContains(response, "Selected only")

    def test_staff_user_gets_photographer_view_for_same_gallery(self):
        user_model = get_user_model()
        staff_user = user_model.objects.create_superuser(
            username="gallery-staff",
            email="gallery-staff@example.com",
            password="pass1234",
        )
        self.client.force_login(staff_user)

        response = self.client.get(self.gallery.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Photographer view")
        self.assertContains(response, "Photographer controls")
        self.assertContains(response, "Open Client Portal")
        self.assertNotContains(response, "Submit Final Selections")

    def test_staff_user_can_open_explicit_photographer_preview_url(self):
        user_model = get_user_model()
        staff_user = user_model.objects.create_superuser(
            username="gallery-preview-staff",
            email="gallery-preview-staff@example.com",
            password="pass1234",
        )
        self.client.force_login(staff_user)

        response = self.client.get(self.gallery.photographer_preview_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Photographer view")
        self.assertContains(response, "Photographer controls")
        self.assertContains(response, self.gallery.client_display_name)

    def test_client_gallery_shows_external_final_delivery_details(self):
        self.gallery.final_delivery_provider = (
            ClientProofingGallery.DELIVERY_PROVIDER_WETRANSFER
        )
        self.gallery.final_delivery_status = ClientProofingGallery.DELIVERY_STATUS_READY
        self.gallery.final_delivery_url = "https://example.com/delivery"
        self.gallery.final_delivery_expires_at = timezone.now() + timedelta(days=7)
        self.gallery.final_delivery_access_note = "Password sent separately."
        self.gallery.final_delivery_note = "Final high-resolution files are delivered externally."
        self.gallery.save()

        session = self.client.session
        session[self.gallery.get_session_access_key()] = str(self.gallery.access_token)
        session.save()

        response = self.client.get(self.gallery.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "WeTransfer")
        self.assertContains(response, "Open Final Delivery Link")
        self.assertContains(response, "Password sent separately.")
        self.assertContains(response, "Final high-resolution files are delivered externally.")


class ProofingAdminTests(TestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        if self.home_page is None:
            root_page = Page.get_first_root_node()
            self.home_page = HomePage(title="Home", slug="home")
            root_page.add_child(instance=self.home_page)

        self.client_record = Client.objects.create(full_name="Sidebar Client")
        self.gallery = ClientProofingGallery(
            title="Sidebar Gallery",
            slug="sidebar-gallery",
            client=self.client_record,
            shoot_date=date(2026, 5, 2),
        )
        self.home_page.add_child(instance=self.gallery)
        self.french_locale = Locale.objects.get_or_create(language_code="fr")[0]

        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            username="proofing-admin",
            email="admin@example.com",
            password="testpass123",
        )
        self.client.force_login(self.admin_user)

    def test_proofing_dashboard_renders_for_admin(self):
        response = self.client.get(reverse("proofing_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Proofing")
        self.assertContains(response, "Sidebar Gallery")
        self.assertContains(response, str(self.gallery.access_token))
        self.assertContains(response, self.gallery.portal_access_path)
        self.assertContains(response, self.gallery.photographer_preview_url)

    def test_proofing_dashboard_lists_translation_group_once(self):
        french_gallery = self.gallery.copy_for_translation(
            self.french_locale,
            copy_parents=True,
        )
        french_gallery.save_revision().publish()

        response = self.client.get(reverse("proofing_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sidebar Gallery", count=1)
