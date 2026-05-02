from datetime import date
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test import RequestFactory, TestCase
from django.urls import reverse

from home.models import HomePage
from proofing.models import ClientProofingGallery, ProofImage
from wagtail.models import Page


GIF_BYTES = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00"
    b"\x00\x00\x00\xff\xff\xff!\xf9\x04"
    b"\x01\x00\x00\x00\x00,\x00\x00\x00"
    b"\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class ClientProofingGalleryAccessTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.home_page = HomePage.objects.first()
        if self.home_page is None:
            root_page = Page.get_first_root_node()
            self.home_page = HomePage(title="Home", slug="home")
            root_page.add_child(instance=self.home_page)
        self.gallery = ClientProofingGallery(
            title="Client Gallery",
            slug="client-gallery",
            client_name="A Client",
            shoot_date=date(2026, 5, 2),
        )
        self.home_page.add_child(instance=self.gallery)

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


class ProofSelectionViewTests(TestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        if self.home_page is None:
            root_page = Page.get_first_root_node()
            self.home_page = HomePage(title="Home", slug="home")
            root_page.add_child(instance=self.home_page)
        self.gallery = ClientProofingGallery(
            title="Client Gallery",
            slug="client-gallery",
            client_name="A Client",
            shoot_date=date(2026, 5, 2),
        )
        self.home_page.add_child(instance=self.gallery)

        from wagtail.images import get_image_model

        image_model = get_image_model()
        self.image = image_model.objects.create(
            title="Proof Image",
            file=SimpleUploadedFile("test.gif", GIF_BYTES, content_type="image/gif"),
        )
        self.proof = ProofImage.objects.create(gallery=self.gallery, image=self.image)

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
