from .base import *

DEBUG = True

EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

# OVERRIDE PRODUCTION STORAGE FOR LOCAL DEVELOPMENT
# This allows standard Django runserver to serve CSS/JS without crashing on missing manifest files.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# 2. Disable WhiteNoise Middleware locally
# This allows Django's runserver to serve files dynamically from STATICFILES_DIRS
MIDDLEWARE = list(MIDDLEWARE)
if "whitenoise.middleware.WhiteNoiseMiddleware" in MIDDLEWARE:
    MIDDLEWARE.remove("whitenoise.middleware.WhiteNoiseMiddleware")

try:
    from .local import *
except ImportError:
    pass
