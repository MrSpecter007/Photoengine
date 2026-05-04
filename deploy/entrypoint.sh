#!/bin/sh
set -eu

APP_USER="${APP_USER:-wagtail}"
MEDIA_DIR="${MEDIA_ROOT:-/app/media}"
STATIC_DIR="${STATIC_ROOT:-/app/staticfiles}"

run_as_app() {
    if [ "$(id -u)" = "0" ]; then
        su "$APP_USER" -s /bin/sh -c "$1"
    else
        sh -c "$1"
    fi
}

if [ "$(id -u)" = "0" ]; then
    mkdir -p "$MEDIA_DIR" "$STATIC_DIR"
    chown -R "$APP_USER":"$APP_USER" "$MEDIA_DIR" "$STATIC_DIR"
fi

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    run_as_app "python manage.py migrate --noinput"
fi

if [ "${RUN_COLLECTSTATIC:-0}" = "1" ]; then
    run_as_app "python manage.py collectstatic --noinput"
fi

if [ "$#" -eq 0 ]; then
    set -- python manage.py runserver 0.0.0.0:8000
fi

if [ "$(id -u)" = "0" ]; then
    exec su "$APP_USER" -s /bin/sh -c "$*"
fi

exec "$@"
