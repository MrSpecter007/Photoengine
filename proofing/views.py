import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from .models import ProofImage


@require_POST
def toggle_proof_selection(request):
    """Toggle a proof selection after verifying gallery access and lock state."""

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid request payload."},
            status=400,
        )

    proof_uuid = data.get("proof_uuid")
    if not proof_uuid:
        return JsonResponse(
            {"status": "error", "message": "Missing proof identifier."},
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
                "message": "You do not have permission to modify this gallery.",
            },
            status=403,
        )

    if proof.gallery.is_locked:
        return JsonResponse(
            {
                "status": "error",
                "message": "Gallery is locked. Selections are finalized.",
            },
            status=403,
        )

    proof.selected_by_client = not proof.selected_by_client
    proof.save(update_fields=["selected_by_client"])

    return JsonResponse(
        {"status": "success", "selected": proof.selected_by_client},
    )
