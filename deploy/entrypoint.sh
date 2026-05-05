#!/bin/sh
set -eu

MEDIA_DIR="${MEDIA_ROOT:-/app/media}"
STATIC_DIR="${STATIC_ROOT:-/app/staticfiles}"

if [ "$(id -u)" = "0" ]; then
    mkdir -p "$MEDIA_DIR" "$STATIC_DIR"
    chown -R wagtail:wagtail "$MEDIA_DIR" "$STATIC_DIR"
fi

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    python manage.py migrate --noinput
fi

if [ "${RUN_COLLECTSTATIC:-0}" = "1" ]; then
    python manage.py collectstatic --noinput
fi

if [ "$#" -eq 0 ]; then
    set -- python manage.py runserver 0.0.0.0:8000
fi

exec "$@"
