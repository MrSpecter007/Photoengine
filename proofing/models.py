import uuid
from pathlib import Path

from django import forms
from django.db import models
from django.http import Http404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import override
from django.utils.http import urlencode

from modelcluster.fields import ParentalKey
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images import get_image_model
from wagtail.models import Orderable, Page
from wagtail.snippets.models import register_snippet

from PhotoEngine.translation_images import TranslationImageSyncMixin


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageFileField(forms.FileField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        return [single_file_clean(item, initial) for item in data]


@register_snippet
class Client(models.Model):
    CONTACT_METHOD_EMAIL = "email"
    CONTACT_METHOD_PHONE = "phone"
    CONTACT_METHOD_TEXT = "text"

    CONTACT_METHOD_CHOICES = [
        (CONTACT_METHOD_EMAIL, "Email"),
        (CONTACT_METHOD_PHONE, "Phone"),
        (CONTACT_METHOD_TEXT, "Text"),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    partner_name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    referral_source = models.CharField(max_length=255, blank=True)
    instagram_handle = models.CharField(max_length=255, blank=True)
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=CONTACT_METHOD_CHOICES,
        default=CONTACT_METHOD_EMAIL,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("full_name"),
        FieldPanel("email"),
        FieldPanel("phone"),
        FieldPanel("partner_name"),
        FieldPanel("address"),
        FieldPanel("referral_source"),
        FieldPanel("instagram_handle"),
        FieldPanel("preferred_contact_method"),
        FieldPanel("notes"),
    ]

    def __str__(self):
        return self.full_name


class ClientProofingGalleryAdminForm(WagtailAdminPageForm):
    bulk_upload_proof_images = MultipleImageFileField(
        required=False,
        help_text=(
            "Upload optimized proof previews only. Keep final high-resolution "
            "deliverables in an external delivery service such as WeTransfer."
        ),
    )

    def save(self, commit=True):
        page = super().save(commit=commit)
        page._pending_bulk_uploads = self.cleaned_data.get("bulk_upload_proof_images") or []
        page._pending_bulk_upload_user = self.for_user
        return page


class ClientProofingGallery(TranslationImageSyncMixin, Page):
    """A token-gated proofing gallery for a specific client."""

    translatable_orderable_relations = {
        "proof_images": {
            "parent_field": "gallery",
            "copy_fields": ("image", "selected_by_client"),
            "follow_fields": ("image",),
            "preserve_fields": ("selected_by_client",),
        },
    }

    STATUS_DRAFT = "draft"
    STATUS_INVITED = "invited"
    STATUS_PROOFING = "proofing"
    STATUS_FINALIZED = "finalized"
    STATUS_DELIVERED = "delivered"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_INVITED, "Invited"),
        (STATUS_PROOFING, "Proofing"),
        (STATUS_FINALIZED, "Finalized"),
        (STATUS_DELIVERED, "Delivered"),
    ]

    DELIVERY_STATUS_NOT_READY = "not_ready"
    DELIVERY_STATUS_READY = "ready"
    DELIVERY_STATUS_SENT = "sent"
    DELIVERY_STATUS_EXPIRED = "expired"
    DELIVERY_STATUS_ARCHIVED = "archived"

    DELIVERY_STATUS_CHOICES = [
        (DELIVERY_STATUS_NOT_READY, "Not ready"),
        (DELIVERY_STATUS_READY, "Ready"),
        (DELIVERY_STATUS_SENT, "Sent"),
        (DELIVERY_STATUS_EXPIRED, "Expired"),
        (DELIVERY_STATUS_ARCHIVED, "Archived"),
    ]

    DELIVERY_PROVIDER_WETRANSFER = "wetransfer"
    DELIVERY_PROVIDER_DROPBOX = "dropbox"
    DELIVERY_PROVIDER_GOOGLE_DRIVE = "google_drive"
    DELIVERY_PROVIDER_OTHER = "other"

    DELIVERY_PROVIDER_CHOICES = [
        (DELIVERY_PROVIDER_WETRANSFER, "WeTransfer"),
        (DELIVERY_PROVIDER_DROPBOX, "Dropbox"),
        (DELIVERY_PROVIDER_GOOGLE_DRIVE, "Google Drive"),
        (DELIVERY_PROVIDER_OTHER, "Other"),
    ]

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

    template = "proofing/client_proofing_gallery.html"
    base_form_class = ClientProofingGalleryAdminForm
    proofs_per_page = 24

    client = models.ForeignKey(
        "proofing.Client",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="proofing_galleries",
    )
    client_name = models.CharField(max_length=255, blank=True)
    invite_email = models.EmailField(blank=True)
    shoot_date = models.DateField()
    shoot_type = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    proof_deadline = models.DateField(null=True, blank=True)
    session_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    package_name = models.CharField(max_length=255, blank=True)
    invoice_reference = models.CharField(max_length=255, blank=True)
    internal_notes = models.TextField(blank=True)
    client_notes = models.TextField(blank=True)
    access_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text="Secure token for gallery access.",
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Lock selections once the client finalizes.",
    )
    presentation_style = models.CharField(
        max_length=32,
        choices=PRESENTATION_STYLE_CHOICES,
        default=PRESENTATION_STYLE_DEFAULT,
    )
    download_link_high_res = models.URLField(
        blank=True,
        help_text="Link to final deliverables.",
    )
    delivery_notes = models.TextField(blank=True)
    final_delivery_provider = models.CharField(
        max_length=32,
        choices=DELIVERY_PROVIDER_CHOICES,
        default=DELIVERY_PROVIDER_WETRANSFER,
        blank=True,
    )
    final_delivery_url = models.URLField(
        blank=True,
        help_text=(
            "External delivery link for final high-resolution files. "
            "Do not upload final originals into PhotoEngine."
        ),
    )
    final_delivery_expires_at = models.DateTimeField(null=True, blank=True)
    final_delivery_access_note = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Optional client-facing note such as 'Password sent separately'."
        ),
    )
    final_delivery_note = models.TextField(
        blank=True,
        help_text="Optional client-facing note about the final delivery.",
    )
    final_delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        default=DELIVERY_STATUS_NOT_READY,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel(
                    "client",
                    help_text="Select the client profile for this proofing gallery.",
                ),
                FieldPanel(
                    "invite_email",
                    heading="Invitation email",
                    help_text=(
                        "Defaults to the selected client's email address. "
                        "Only set this if the invite should go to a different address."
                    ),
                ),
                FieldPanel("shoot_date"),
                FieldPanel("shoot_type"),
                FieldPanel("location"),
                FieldPanel("proof_deadline"),
                FieldPanel("session_status"),
            ],
            heading="Client & Session",
        ),
        MultiFieldPanel(
            [
                FieldPanel("package_name"),
                FieldPanel("invoice_reference"),
                FieldPanel("internal_notes"),
                FieldPanel("client_notes"),
            ],
            heading="CRM Details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("presentation_style"),
                FieldPanel("is_locked"),
                FieldPanel("final_delivery_provider"),
                FieldPanel("final_delivery_status"),
                FieldPanel("final_delivery_url"),
                FieldPanel("final_delivery_expires_at"),
                FieldPanel("final_delivery_access_note"),
                FieldPanel("final_delivery_note"),
            ],
            heading="Proofing & Delivery",
        ),
        MultiFieldPanel(
            [
                FieldPanel("bulk_upload_proof_images"),
                InlinePanel("proof_images", label="Proof Images"),
            ],
            heading="Proof Images",
        ),
    ]

    @property
    def client_display_name(self):
        if self.client:
            return self.client.full_name
        return self.client_name or self.title

    @property
    def body_class(self):
        if self.presentation_style == self.PRESENTATION_STYLE_ANIMATE_SCROLL_3:
            return "animate-scroll-3"
        return ""

    @property
    def uses_progressive_loading(self):
        return self.presentation_style in {
            self.PRESENTATION_STYLE_DEFAULT,
            self.PRESENTATION_STYLE_GRID,
            self.PRESENTATION_STYLE_MASONRY,
        }

    def save(self, *args, **kwargs):
        previous_state = self.capture_translation_image_sync_state()
        skip_sync = getattr(self, "_skip_translation_image_sync", False)
        if self.client:
            self.client_name = self.client.full_name
        if self.client and not self.invite_email and self.client.email:
            self.invite_email = self.client.email
        result = super().save(*args, **kwargs)
        if skip_sync:
            self._skip_translation_image_sync = False
            return result
        self.sync_translated_images(previous_state)
        return result

    def attach_uploaded_images(self, uploaded_files, user=None):
        previous_state = self.capture_translation_image_sync_state(include_relations=True)
        image_model = get_image_model()
        existing_proofs = list(self.proof_images.all())
        sort_base = max((proof.sort_order or 0 for proof in existing_proofs), default=0)

        for index, uploaded_file in enumerate(uploaded_files, start=1):
            image = image_model(
                title=Path(uploaded_file.name).stem,
                file=uploaded_file,
                uploaded_by_user=user if getattr(user, "is_authenticated", False) else None,
            )
            image.save()

            self.proof_images.add(
                ProofImage(
                    gallery=self,
                    image=image,
                    sort_order=sort_base + index,
                )
            )

        self.sync_translated_images(previous_state, include_relations=True)

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

    def get_session_access_key(self):
        return f"proofing_gallery_access_{self.translation_key}"

    def translation_group(self):
        return type(self).objects.filter(translation_key=self.translation_key)

    def get_localized_url(self, language_code):
        if self.locale.language_code == language_code:
            return self.url

        translated = self.translation_group().filter(locale__language_code=language_code).first()
        if translated is not None:
            return translated.url

        return self.url

    @property
    def portal_access_path(self):
        base_url = self.url or reverse("proofing:portal")
        query_string = urlencode({"token": str(self.access_token)})
        return f"{base_url}?{query_string}"

    @property
    def photographer_preview_url(self):
        return reverse("proofing:photographer_preview", args=[self.pk])

    @property
    def delivery_download_url(self):
        return self.final_delivery_url or self.download_link_high_res

    @property
    def delivery_note_display(self):
        return self.final_delivery_note or self.delivery_notes

    @property
    def delivery_provider_display_name(self):
        provider = self.final_delivery_provider or self.DELIVERY_PROVIDER_WETRANSFER
        return dict(self.DELIVERY_PROVIDER_CHOICES).get(provider, "External provider")

    @property
    def delivery_is_ready(self):
        if self.delivery_is_expired:
            return False
        if self.final_delivery_status in {
            self.DELIVERY_STATUS_READY,
            self.DELIVERY_STATUS_SENT,
        } and self.delivery_download_url:
            return True
        return bool(self.download_link_high_res and not self.final_delivery_url)

    @property
    def delivery_is_expired(self):
        if self.final_delivery_status == self.DELIVERY_STATUS_EXPIRED:
            return True
        if self.final_delivery_expires_at:
            return self.final_delivery_expires_at <= timezone.now()
        return False

    def localized_portal_access_path(self, language_code):
        base_url = self.get_localized_url(language_code)
        query_string = urlencode({"token": str(self.access_token)})
        return f"{base_url}?{query_string}"

    def localized_photographer_preview_url(self, language_code):
        localized_gallery = self.translation_group().filter(
            locale__language_code=language_code
        ).first() or self
        with override(language_code):
            return reverse("proofing:photographer_preview", args=[localized_gallery.pk])

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

    def get_proof_page(self, page_number=1):
        paginator = Paginator(
            self.proof_images.select_related("image").all(),
            self.proofs_per_page,
        )

        try:
            return paginator.page(page_number)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        proof_page = self.get_proof_page(page_number=1)
        if self.uses_progressive_loading:
            proof_images = proof_page.object_list
        else:
            proof_images = self.proof_images.select_related("image").all()

        context["proof_images"] = proof_images
        context["proof_page"] = proof_page
        context["uses_progressive_loading"] = self.uses_progressive_loading
        context["selected_count"] = self.proof_images.filter(selected_by_client=True).count()
        context["is_photographer_view"] = bool(
            getattr(request, "user", None)
            and request.user.is_authenticated
            and request.user.is_staff
        )
        context["show_client_selection_controls"] = (
            not context["is_photographer_view"] and not self.is_locked
        )
        context["client_portal_url"] = self.portal_access_path
        context["photographer_preview_url"] = self.photographer_preview_url
        context["photographer_edit_url"] = reverse(
            "wagtailadmin_pages:edit",
            args=[self.pk],
        )
        context["toggle_selection_url"] = reverse("proofing:toggle_selection")
        context["finalize_selection_url"] = reverse("proofing:finalize_selection")
        context["load_more_url"] = reverse("proofing:load_more_proofs")
        return context

    def sync_client_selection(self, image_id, is_selected):
        for gallery in self.translation_group().specific():
            gallery.proof_images.filter(image_id=image_id).update(
                selected_by_client=is_selected
            )

    def sync_lock_state(self, *, is_locked, session_status):
        self.translation_group().update(
            is_locked=is_locked,
            session_status=session_status,
        )


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

    def save(self, *args, **kwargs):
        if self.proof_uuid and type(self).objects.exclude(pk=self.pk).filter(
            proof_uuid=self.proof_uuid
        ).exists():
            self.proof_uuid = uuid.uuid4()
        return super().save(*args, **kwargs)
