from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from home.models import ContactPage, HomePage

from .models import (
    EditionFormat,
    PhotoCollection,
    Photograph,
    PhotographEdition,
    PrintSize,
)


def _contact_page(request):
    language_code = getattr(request, "LANGUAGE_CODE", "en")
    site = getattr(request, "site", None)

    if site and getattr(site, "root_page", None):
        homepage = site.root_page.specific
        if isinstance(homepage, HomePage):
            contact = ContactPage.objects.descendant_of(homepage).live().public().first()
            if contact:
                return contact

    return (
        ContactPage.objects.live()
        .public()
        .filter(locale__language_code=language_code)
        .first()
        or ContactPage.objects.live().public().first()
    )


def _available_print_sizes(photograph):
    sizes = list(
        PrintSize.objects.filter(
            is_active=True,
            aspect_ratio=photograph.native_ratio,
        )
    )
    if sizes:
        return sizes
    return list(PrintSize.objects.filter(is_active=True))


def edition_catalog(request):
    active_photographs = (
        Photograph.objects.filter(is_active=True)
        .select_related("collection")
        .prefetch_related("editions")
        .order_by("collection__title", "title")
    )
    collections = (
        PhotoCollection.objects.filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "photographs",
                queryset=active_photographs,
                to_attr="active_photographs",
            )
        )
        .order_by("launch_date", "title")
    )

    return render(
        request,
        "editions/catalog.html",
        {
            "collections": collections,
            "formats": EditionFormat.objects.filter(is_active=True),
            "contact_page": _contact_page(request),
        },
    )


def photograph_detail(request, collection_slug, photograph_slug):
    photograph = get_object_or_404(
        Photograph.objects.select_related("collection").prefetch_related("editions"),
        collection__slug=collection_slug,
        slug=photograph_slug,
        collection__is_active=True,
        is_active=True,
    )

    return render(
        request,
        "editions/photograph_detail.html",
        {
            "photograph": photograph,
            "formats": EditionFormat.objects.filter(is_active=True),
            "sizes": _available_print_sizes(photograph),
            "contact_page": _contact_page(request),
            "available_editions": photograph.editions.filter(
                edition_type=PhotographEdition.EDITION_PUBLIC,
                status=PhotographEdition.STATUS_AVAILABLE,
            ),
        },
    )
