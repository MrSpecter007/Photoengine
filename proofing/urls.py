from django.urls import path

from .views import toggle_proof_selection

app_name = "proofing"

urlpatterns = [
    path("toggle-selection/", toggle_proof_selection, name="toggle_selection"),
]
