from django.shortcuts import render

from home.models import ContactPage, HomePage


def _get_contact_page(request):
    language_code = getattr(request, "LANGUAGE_CODE", "en")
    site = getattr(request, "site", None)

    if site and getattr(site, "root_page", None):
        homepage = site.root_page.specific
        if not isinstance(homepage, HomePage):
            homepage = (
                HomePage.objects.in_site(site)
                .live()
                .public()
                .filter(locale__language_code=language_code)
                .first()
            )
        if homepage:
            page = ContactPage.objects.descendant_of(homepage).live().public().first()
            if page:
                return page

    return (
        ContactPage.objects.live()
        .public()
        .filter(locale__language_code=language_code)
        .first()
        or ContactPage.objects.live().public().first()
    )


def privacy_policy(request):
    """Site-wide privacy policy for the public website and contact form."""

    return render(
        request,
        "home/privacy_policy.html",
        {
            "contact_page": _get_contact_page(request),
        },
    )
