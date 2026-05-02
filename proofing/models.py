import uuid

from django.db import models
from django.http import Http404
from django.urls import reverse

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Orderable, Page


class ClientProofingGallery(Page):
    """A token-gated proofing gallery for a specific client."""

    template = "proofing/client_proofing_gallery.html"

    client_name = models.CharField(max_length=255)
    shoot_date = models.DateField()
    access_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text="Secure token for gallery access.",
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Lock selections once the client finalizes.",
    )
    download_link_high_res = models.URLField(
        blank=True,
        help_text="Link to final deliverables.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("client_name"),
        FieldPanel("shoot_date"),
        FieldPanel("is_locked"),
        FieldPanel("download_link_high_res"),
        InlinePanel("proof_images", label="Proof Images"),
    ]

    def get_session_access_key(self):
        return f"proofing_gallery_access_{self.pk}"

    def request_has_access(self, request, provided_token=None):
        if getattr(request, "user", None) and request.user.is_authenticated and request.user.is_staff:
            return True

        expected_token = str(self.access_token)
        session_key = self.get_session_access_key()
        stored_token = request.session.get(session_key)

        if stored_token == expected_token:
            return True

        if provided_token and str(provided_token) == expected_token:
            request.session[session_key] = expected_token
            return True

        return False

    def serve(self, request, *args, **kwargs):
        provided_token = request.GET.get("token")
        if not self.request_has_access(request, provided_token=provided_token):
            raise Http404("Gallery not found.")
        return super().serve(request, *args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["proof_images"] = self.proof_images.select_related("image").all()
        context["selected_count"] = self.proof_images.filter(selected_by_client=True).count()
        context["toggle_selection_url"] = reverse("proofing:toggle_selection")
        return context


class ProofImage(Orderable):
    """Individual proof images attached to a specific client gallery."""

    gallery = ParentalKey(
        "proofing.ClientProofingGallery",
        related_name="proof_images",
        on_delete=models.CASCADE,
    )
    proof_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
    )
    selected_by_client = models.BooleanField(default=False)

    panels = [
        FieldPanel("image"),
        FieldPanel("selected_by_client"),
    ]
