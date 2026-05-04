from django.urls import path

from .views import (
    finalize_proof_selection,
    load_more_proofs,
    photographer_preview,
    proofing_legal,
    proofing_portal,
    toggle_proof_selection,
)

app_name = "proofing"

urlpatterns = [
    path("", proofing_portal, name="portal"),
    path("legal/", proofing_legal, name="legal"),
    path(
        "photographer-preview/<int:gallery_id>/",
        photographer_preview,
        name="photographer_preview",
    ),
    path("toggle-selection/", toggle_proof_selection, name="toggle_selection"),
    path("finalize-selection/", finalize_proof_selection, name="finalize_selection"),
    path("load-more-proofs/", load_more_proofs, name="load_more_proofs"),
]
