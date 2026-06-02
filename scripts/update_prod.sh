#!/bin/sh
set -eu

compose() {
    docker compose -f docker-compose.prod.yml "$@"
}

wait_for_web() {
    web_id="$(compose ps -q web)"
    if [ -z "$web_id" ]; then
        echo "Could not determine the web container id." >&2
        exit 1
    fi

    timeout_seconds="${DEPLOY_HEALTH_TIMEOUT:-180}"
    elapsed=0

    echo "Waiting for web to report healthy..."
    while :; do
        status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$web_id" 2>/dev/null || true)"

        case "$status" in
            healthy)
                echo "Web is healthy."
                return 0
                ;;
            unhealthy)
                echo "Web reported unhealthy. Recent logs:" >&2
                compose logs web --tail=120 >&2
                exit 1
                ;;
        esac

        if [ "$elapsed" -ge "$timeout_seconds" ]; then
            echo "Timed out waiting for the web service to become healthy." >&2
            compose logs web --tail=120 >&2
            exit 1
        fi

        sleep 5
        elapsed=$((elapsed + 5))
    done
}

echo "Building production images..."
compose build

echo "Starting database, redis, web, and celery..."
compose up -d db redis web celery

wait_for_web

echo "Refreshing nginx after web is healthy..."
compose up -d nginx

echo "Current production status:"
compose ps

echo "Recent web logs:"
compose logs web --tail=60
