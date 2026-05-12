from django import template
from django.utils.translation import get_language

from home.models import (
    ContactPage,
    GalleryPage,
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
    current_page = context.get("page")
    if current_page is not None:
        current_page = getattr(current_page, "specific", current_page)
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
    portfolio_menu = []
    active_portfolio_key = None
    current_page_path = getattr(current_page, "path", "")
    if portfolio_page:
        portfolio_categories = list(
            PortfolioCategoryPage.objects.child_of(portfolio_page)
            .live()
            .public()
            .order_by("path")
        )
        for index, category in enumerate(portfolio_categories):
            galleries = list(
                GalleryPage.objects.child_of(category)
                .live()
                .public()
                .order_by("path")
            )
            category_key = f"category-{category.id}"
            is_active = bool(current_page_path and current_page_path.startswith(category.path))
            if is_active:
                active_portfolio_key = category_key

            portfolio_menu.append(
                {
                    "key": category_key,
                    "page": category,
                    "galleries": galleries,
                    "is_active": is_active,
                    "is_default": index == 0,
                }
            )

    if portfolio_menu and active_portfolio_key is None:
        default_item = next((item for item in portfolio_menu if item["galleries"]), portfolio_menu[0])
        active_portfolio_key = default_item["key"]
        default_item["is_active"] = True

    has_portfolio_children = any(item["galleries"] for item in portfolio_menu)

    return {
        "home": homepage,
        "portfolio": portfolio_page,
        "portfolio_categories": portfolio_categories,
        "portfolio_menu": portfolio_menu,
        "active_portfolio_key": active_portfolio_key,
        "has_portfolio_children": has_portfolio_children,
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
