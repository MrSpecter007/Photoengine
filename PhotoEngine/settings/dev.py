from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-!86k82%gjmwie0+2@j0a+6+s5i20vpx$t4&_kj(-!^-mm_&r&+"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

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
