from django.utils.translation import get_language


def is_french(language_code=None):
    code = (language_code or get_language() or "").lower()
    return code.startswith("fr")


def choose_translation(*, en, fr, language_code=None):
    return fr if is_french(language_code) else en
