from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.translation import get_language, override

from wagtail.models import Locale, Page

from home.i18n import choose_translation

register = template.Library()


def _get_context_language(context):
    request = context.get("request")
    return (
        context.get("LANGUAGE_CODE")
        or getattr(request, "LANGUAGE_CODE", None)
        or get_language()
        or "en"
    )


def _get_page_translation_url(page, language_code):
    if not page or not isinstance(page, Page):
        return None

    locale = Locale.objects.filter(language_code=language_code).first()
    if locale is None:
        return None

    if page.locale_id == locale.id:
        return page.url

    try:
        translation = page.get_translation(locale)
    except Page.DoesNotExist:
        return None

    if translation.live:
        return translation.url

    return None


def _get_language_specific_route(request, language_code):
    resolver_match = getattr(request, "resolver_match", None)
    if resolver_match is None:
        return None

    route_name = resolver_match.view_name
    kwargs = resolver_match.kwargs or {}

    if route_name == "proofing:portal":
        with override(language_code):
            return reverse("proofing:portal")

    if route_name == "proofing:legal":
        with override(language_code):
            return reverse("proofing:legal")

    if route_name == "privacy_policy":
        with override(language_code):
            return reverse("privacy_policy")

    if route_name == "search":
        with override(language_code):
            return reverse("search")

    if route_name == "proofing:photographer_preview":
        with override(language_code):
            return reverse("proofing:photographer_preview", kwargs=kwargs)

    return None


@register.simple_tag(takes_context=True)
def tr(context, en, fr):
    return choose_translation(
        en=en,
        fr=fr,
        language_code=_get_context_language(context),
    )


@register.simple_tag(takes_context=True)
def get_language_switcher(context):
    request = context.get("request")
    page = context.get("page")
    current_language = _get_context_language(context)
    site = getattr(request, "site", None)
    fallback_root = getattr(site, "root_page", None)

    links = []
    for code, label in (("en", "EN"), ("fr", "FR")):
        url = _get_page_translation_url(page, code)

        if url is None and request is not None:
            url = _get_language_specific_route(request, code)

        if url is None and fallback_root is not None:
            url = _get_page_translation_url(fallback_root.specific, code)

        if url is None:
            with override(code):
                try:
                    url = reverse("wagtail_serve", args=[""])
                except NoReverseMatch:
                    url = "/" if code == "en" else f"/{code}/"

        links.append(
            {
                "code": code,
                "label": label,
                "url": url,
                "is_active": current_language.startswith(code),
            }
        )

    return {"current_language": current_language, "links": links}
