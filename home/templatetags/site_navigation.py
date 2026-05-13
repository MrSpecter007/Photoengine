from django import template
from django.utils.translation import get_language

from home.models import (
    AboutPage,
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
    resolver_match = getattr(request, "resolver_match", None)
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
        about_page = AboutPage.objects.descendant_of(homepage).live().public().first()
        portfolio_page = (
            PortfolioIndexPage.objects.descendant_of(homepage).live().public().first()
        )
        contact_page = ContactPage.objects.descendant_of(homepage).live().public().first()
    else:
        about_page = AboutPage.objects.live().public().first()
        portfolio_page = PortfolioIndexPage.objects.live().public().first()
        contact_page = ContactPage.objects.live().public().first()

    portfolio_categories = []
    portfolio_menu = []
    active_portfolio_key = None
    current_page_path = getattr(current_page, "path", "")
    current_page_id = getattr(current_page, "id", None)
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
                    "galleries": [
                        {
                            "page": gallery,
                            "is_active": bool(
                                current_page_path and current_page_path.startswith(gallery.path)
                            ),
                        }
                        for gallery in galleries
                    ],
                    "is_active": is_active,
                    "is_default": index == 0,
                }
            )

    if portfolio_menu and active_portfolio_key is None:
        default_item = next((item for item in portfolio_menu if item["galleries"]), portfolio_menu[0])
        active_portfolio_key = default_item["key"]
        default_item["is_active"] = True

    has_portfolio_children = any(item["galleries"] for item in portfolio_menu)
    active_portfolio_item = next(
        (item for item in portfolio_menu if item["key"] == active_portfolio_key),
        portfolio_menu[0] if portfolio_menu else None,
    )
    home_is_active = bool(homepage and current_page_id == homepage.id)
    about_is_active = bool(about_page and current_page_path and current_page_path.startswith(about_page.path))
    portfolio_is_active = bool(
        portfolio_page
        and current_page_path
        and current_page_path.startswith(portfolio_page.path)
    )
    contact_is_active = bool(
        contact_page and current_page_path and current_page_path.startswith(contact_page.path)
    )
    proofing_is_active = bool(resolver_match and resolver_match.namespace == "proofing")

    return {
        "home": homepage,
        "home_is_active": home_is_active,
        "about": about_page,
        "about_is_active": about_is_active,
        "portfolio": portfolio_page,
        "portfolio_is_active": portfolio_is_active,
        "portfolio_categories": portfolio_categories,
        "portfolio_menu": portfolio_menu,
        "active_portfolio_key": active_portfolio_key,
        "active_portfolio_item": active_portfolio_item,
        "has_portfolio_children": has_portfolio_children,
        "contact": contact_page,
        "contact_is_active": contact_is_active,
        "proofing_is_active": proofing_is_active,
        "labels": {
            "home": choose_translation(en="Home", fr="Accueil", language_code=current_language),
            "portfolio": choose_translation(
                en="Portfolio",
                fr="Portfolio",
                language_code=current_language,
            ),
            "about": choose_translation(
                en="About",
                fr="A propos",
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
