from django import template
from django.utils.translation import get_language

from home.models import (
    ContactPage,
    HomePage,
    PortfolioCategoryPage,
    PortfolioIndexPage,
)
from home.i18n import choose_translation

register = template.Library()


def _localized_or_self(page):
    if not page:
        return None

    localized = getattr(page, "localized", None)
    return localized if localized is not None else page


@register.simple_tag(takes_context=True)
def get_site_navigation(context):
    request = context.get("request")
    current_language = (
        getattr(request, "LANGUAGE_CODE", None)
        or context.get("LANGUAGE_CODE")
        or get_language()
        or "en"
    )

    homepage = HomePage.objects.live().public().filter(locale__language_code=current_language).first()
    if request and getattr(request, "site", None):
        homepage = _localized_or_self(request.site.root_page.specific)
        if not isinstance(homepage, HomePage):
            homepage = (
                HomePage.objects.in_site(request.site)
                .live()
                .public()
                .filter(locale__language_code=current_language)
                .first()
                or homepage
            )

    if homepage:
        portfolio_page = (
            PortfolioIndexPage.objects.descendant_of(homepage).live().public().first()
        )
        contact_page = ContactPage.objects.descendant_of(homepage).live().public().first()
    else:
        portfolio_page = PortfolioIndexPage.objects.live().public().first()
        contact_page = ContactPage.objects.live().public().first()

    portfolio_categories = []
    portfolio_sections = []
    if portfolio_page:
        portfolio_categories = list(
            PortfolioCategoryPage.objects.child_of(portfolio_page).live().public()
        )
        portfolio_sections = [
            {
                "page": category,
                "galleries": [
                    {"page": gallery}
                    for gallery in category.get_children().live().public().specific()
                ],
            }
            for category in portfolio_categories
        ]

    return {
        "home": homepage,
        "portfolio": portfolio_page,
        "portfolio_categories": portfolio_categories,
        "portfolio_sections": portfolio_sections,
        "contact": contact_page,
        "labels": {
            "home": choose_translation(en="Home", fr="Accueil", language_code=current_language),
            "portfolio": choose_translation(
                en="Portfolio",
                fr="Portfolio",
                language_code=current_language,
            ),
            "all_portfolio": choose_translation(
                en="All Portfolio",
                fr="Tout le portfolio",
                language_code=current_language,
            ),
            "proofing_portal": choose_translation(
                en="Proofing Portal",
                fr="Portail évaluation",
                language_code=current_language,
            ),
            "contact": choose_translation(
                en="Contact",
                fr="Contact",
                language_code=current_language,
            ),
        },
    }
