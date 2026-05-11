FROM python:3.12-slim-bookworm

RUN useradd -m wagtail

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=PhotoEngine.settings.dev

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "setuptools>=70,<82" "gunicorn==20.0.4"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY . /app
COPY deploy/entrypoint.sh /entrypoint.sh

RUN sed -i 's/\r//' /entrypoint.sh && chmod +x /entrypoint.sh && chown -R wagtail:wagtail /app

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
