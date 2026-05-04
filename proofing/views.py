import json
from uuid import UUID

from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from wagtail.admin.auth import require_admin_access

from home.i18n import choose_translation
from .forms import ProofingPortalAccessForm
from .models import ClientProofingGallery, ProofImage


def _proofing_copy(language_code):
    return {
        "invalid_token": choose_translation(
            en="Enter a valid proofing access token from your invite email.",
            fr="Entrez un jeton d'acces valide provenant de votre courriel d'invitation.",
            language_code=language_code,
        ),
        "token_not_found": choose_translation(
            en="We couldn't find a proofing gallery for that token.",
            fr="Aucune galerie d'epreuves n'a ete trouvee pour ce jeton.",
            language_code=language_code,
        ),
        "invalid_payload": choose_translation(
            en="Invalid request payload.",
            fr="Le contenu de la requete est invalide.",
            language_code=language_code,
        ),
        "missing_proof_identifier": choose_translation(
            en="Missing proof identifier.",
            fr="Identifiant d'epreuve manquant.",
            language_code=language_code,
        ),
        "no_modify_permission": choose_translation(
            en="You do not have permission to modify this gallery.",
            fr="Vous n'avez pas l'autorisation de modifier cette galerie.",
            language_code=language_code,
        ),
        "gallery_locked": choose_translation(
            en="Gallery is locked. Selections are finalized.",
            fr="La galerie est verrouillee. Les selections sont finalisees.",
            language_code=language_code,
        ),
        "missing_gallery_identifier": choose_translation(
            en="Missing gallery identifier.",
            fr="Identifiant de galerie manquant.",
            language_code=language_code,
        ),
        "no_finalize_permission": choose_translation(
            en="You do not have permission to finalize this gallery.",
            fr="Vous n'avez pas l'autorisation de finaliser cette galerie.",
            language_code=language_code,
        ),
        "already_finalized": choose_translation(
            en="Gallery is already finalized.",
            fr="La galerie est deja finalisee.",
            language_code=language_code,
        ),
        "select_before_finalizing": choose_translation(
            en="Select at least one image before finalizing.",
            fr="Selectionnez au moins une image avant de finaliser.",
            language_code=language_code,
        ),
        "submitted_message": choose_translation(
            en="Your selections have been submitted.",
            fr="Vos selections ont ete envoyees.",
            language_code=language_code,
        ),
        "no_view_permission": choose_translation(
            en="You do not have permission to view this gallery.",
            fr="Vous n'avez pas l'autorisation de voir cette galerie.",
            language_code=language_code,
        ),
        "invalid_page_number": choose_translation(
            en="Invalid page number.",
            fr="Numero de page invalide.",
            language_code=language_code,
        ),
    }


def proofing_portal(request):
    """Public entry point for clients to access a token-gated proofing gallery."""

    language_code = getattr(request, "LANGUAGE_CODE", "en")
    copy = _proofing_copy(language_code)
    form = ProofingPortalAccessForm(request.POST or None, language_code=language_code)

    if request.method == "POST" and form.is_valid():
        raw_token = (form.cleaned_data.get("access_token") or "").strip()

        try:
            normalized_token = str(UUID(raw_token))
        except (ValueError, TypeError):
            form.add_error("access_token", copy["invalid_token"])
        else:
            galleries = ClientProofingGallery.objects.live().public().filter(
                access_token=normalized_token
            )
            gallery = galleries.filter(locale__language_code=language_code).first() or galleries.first()

            if gallery is None:
                form.add_error("access_token", copy["token_not_found"])
            else:
                return redirect(f"{gallery.url}?token={normalized_token}")

    return render(
        request,
        "proofing/portal_entry.html",
        {
            "form": form,
        },
    )


def proofing_legal(request):
    """Public legal and privacy information for the proofing portal."""

    return render(request, "proofing/legal.html")


@require_admin_access
def photographer_preview(request, gallery_id):
    """Explicit staff-only preview of the same gallery instance."""

    gallery = get_object_or_404(
        ClientProofingGallery.objects.live().public().specific(),
        pk=gallery_id,
    )
    context = gallery.get_context(request)
    return render(request, gallery.template, context)


@require_POST
def toggle_proof_selection(request):
    """Toggle a proof selection after verifying gallery access and lock state."""

    copy = _proofing_copy(getattr(request, "LANGUAGE_CODE", "en"))

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": copy["invalid_payload"]},
            status=400,
        )

    proof_uuid = data.get("proof_uuid")
    if not proof_uuid:
        return JsonResponse(
            {"status": "error", "message": copy["missing_proof_identifier"]},
            status=400,
        )

    proof = get_object_or_404(
        ProofImage.objects.select_related("gallery"),
        proof_uuid=proof_uuid,
    )

    if not proof.gallery.request_has_access(request, provided_token=data.get("access_token")):
        return JsonResponse(
            {
                "status": "error",
                "message": copy["no_modify_permission"],
            },
            status=403,
        )

    if proof.gallery.is_locked:
        return JsonResponse(
            {
                "status": "error",
                "message": copy["gallery_locked"],
            },
            status=403,
        )

    proof.selected_by_client = not proof.selected_by_client
    proof.save(update_fields=["selected_by_client"])
    proof.gallery.sync_client_selection(proof.image_id, proof.selected_by_client)

    return JsonResponse(
        {"status": "success", "selected": proof.selected_by_client},
    )


@require_POST
def finalize_proof_selection(request):
    """Lock the gallery after the client confirms their selections."""

    copy = _proofing_copy(getattr(request, "LANGUAGE_CODE", "en"))

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": copy["invalid_payload"]},
            status=400,
        )

    gallery_id = data.get("gallery_id")
    if not gallery_id:
        return JsonResponse(
            {"status": "error", "message": copy["missing_gallery_identifier"]},
            status=400,
        )

    gallery = get_object_or_404(ClientProofingGallery, pk=gallery_id)

    if not gallery.request_has_access(request, provided_token=data.get("access_token")):
        return JsonResponse(
            {
                "status": "error",
                "message": copy["no_finalize_permission"],
            },
            status=403,
        )

    if gallery.is_locked:
        return JsonResponse(
            {
                "status": "error",
                "message": copy["already_finalized"],
            },
            status=403,
        )

    selected_count = gallery.proof_images.filter(selected_by_client=True).count()
    if selected_count == 0:
        return JsonResponse(
            {
                "status": "error",
                "message": copy["select_before_finalizing"],
            },
            status=400,
        )

    gallery.sync_lock_state(
        is_locked=True,
        session_status=ClientProofingGallery.STATUS_FINALIZED,
    )

    return JsonResponse(
        {
            "status": "success",
            "selected_count": selected_count,
            "message": copy["submitted_message"],
        }
    )


@require_GET
def load_more_proofs(request):
    """Progressively load additional proof cards for authorized galleries."""

    copy = _proofing_copy(getattr(request, "LANGUAGE_CODE", "en"))
    gallery_id = request.GET.get("gallery_id")
    page_number = request.GET.get("page", 1)
    access_token = request.GET.get("token")

    if not gallery_id:
        return JsonResponse(
            {"status": "error", "message": copy["missing_gallery_identifier"]},
            status=400,
        )

    gallery = get_object_or_404(ClientProofingGallery, pk=gallery_id)

    if not gallery.request_has_access(request, provided_token=access_token):
        return JsonResponse(
            {
                "status": "error",
                "message": copy["no_view_permission"],
            },
            status=403,
        )

    try:
        proof_page = gallery.get_proof_page(page_number=page_number)
    except (TypeError, ValueError):
        return JsonResponse(
            {"status": "error", "message": copy["invalid_page_number"]},
            status=400,
        )

    html = render_to_string(
        "proofing/includes/proof_image_items.html",
        {
            "page": gallery,
            "proof_images": proof_page.object_list,
            "show_client_selection_controls": (
                not (
                    getattr(request, "user", None)
                    and request.user.is_authenticated
                    and request.user.is_staff
                )
                and not gallery.is_locked
            ),
        },
        request=request,
    )

    return JsonResponse(
        {
            "status": "success",
            "html": html,
            "has_next": proof_page.has_next(),
            "next_page": proof_page.next_page_number() if proof_page.has_next() else None,
        }
    )
