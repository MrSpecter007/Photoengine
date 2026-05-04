import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PhotoEngine.settings.dev")

app = Celery("PhotoEngine")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
