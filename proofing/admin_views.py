from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import reverse

from home.models import HomePage
from proofing.models import Client, ClientProofingGallery


def proofing_dashboard(request):
    galleries = (
        ClientProofingGallery.objects.live()
        .public()
        .filter(locale__language_code="en")
        .specific()
        .select_related("client")
        .annotate(
            selected_count=Count(
                "proof_images",
                filter=Q(proof_images__selected_by_client=True),
            ),
            proof_count=Count("proof_images"),
        )
        .order_by("-shoot_date", "title")
    )

    home_page = HomePage.objects.filter(locale__language_code="en").first()
    add_gallery_url = (
        reverse("wagtailadmin_pages:add_subpage", args=[home_page.pk])
        if home_page
        else reverse("wagtailadmin_explore_root")
    )

    context = {
        "galleries": galleries,
        "gallery_count": galleries.count(),
        "client_count": Client.objects.count(),
        "clients_url": reverse("wagtailsnippets_proofing_client:list"),
        "add_gallery_url": add_gallery_url,
    }
    return render(request, "proofing/admin/dashboard.html", context)
