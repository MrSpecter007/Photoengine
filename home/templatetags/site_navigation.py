from django import template
from django.utils.translation import get_language

from home.models import (
    ArtifactIndexPage,
    CollaboratePage,
    ContactPage,
    FieldNotesIndexPage,
    HomePage,
    LabPage,
    PortfolioCategoryPage,
    PortfolioIndexPage,
    StudyIndexPage,
    WorldPage,
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
        studies_page = StudyIndexPage.objects.descendant_of(homepage).live().public().first()
        artifacts_page = ArtifactIndexPage.objects.descendant_of(homepage).live().public().first()
        field_notes_page = FieldNotesIndexPage.objects.descendant_of(homepage).live().public().first()
        lab_page = LabPage.objects.descendant_of(homepage).live().public().first()
        world_page = WorldPage.objects.descendant_of(homepage).live().public().first()
        collaborate_page = CollaboratePage.objects.descendant_of(homepage).live().public().first()
        # Legacy
        portfolio_page = PortfolioIndexPage.objects.descendant_of(homepage).live().public().first()
        contact_page = ContactPage.objects.descendant_of(homepage).live().public().first()
    else:
        studies_page = StudyIndexPage.objects.live().public().first()
        artifacts_page = ArtifactIndexPage.objects.live().public().first()
        field_notes_page = FieldNotesIndexPage.objects.live().public().first()
        lab_page = LabPage.objects.live().public().first()
        world_page = WorldPage.objects.live().public().first()
        collaborate_page = CollaboratePage.objects.live().public().first()
        portfolio_page = PortfolioIndexPage.objects.live().public().first()
        contact_page = ContactPage.objects.live().public().first()

    portfolio_categories = []
    if portfolio_page:
        portfolio_categories = list(
            PortfolioCategoryPage.objects.child_of(portfolio_page).live().public()
        )

    return {
        "home": homepage,
        # Specter Vision primary nav
        "studies": studies_page,
        "artifacts": artifacts_page,
        "field_notes": field_notes_page,
        "lab": lab_page,
        "world": world_page,
        "collaborate": collaborate_page,
        # Legacy (for proofing portal and internal use)
        "portfolio": portfolio_page,
        "portfolio_categories": portfolio_categories,
        "contact": contact_page,
        "labels": {
            "home": choose_translation(en="Home", fr="Accueil", language_code=current_language),
            "studies": choose_translation(en="Studies", fr="Études", language_code=current_language),
            "artifacts": choose_translation(en="Artifacts", fr="Artefacts", language_code=current_language),
            "field_notes": choose_translation(en="Field Notes", fr="Notes de terrain", language_code=current_language),
            "lab": choose_translation(en="The Lab", fr="Le Lab", language_code=current_language),
            "world": choose_translation(en="World", fr="Monde", language_code=current_language),
            "collaborate": choose_translation(en="Collaborate", fr="Collaborer", language_code=current_language),
            "portfolio": choose_translation(en="Portfolio", fr="Portfolio", language_code=current_language),
            "all_portfolio": choose_translation(en="All Portfolio", fr="Tout le portfolio", language_code=current_language),
            "proofing_portal": choose_translation(en="Proofing Portal", fr="Portail évaluation", language_code=current_language),
            "contact": choose_translation(en="Contact", fr="Contact", language_code=current_language),
        },
    }
