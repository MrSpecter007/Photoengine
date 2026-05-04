# PhotoEngine Deployment

## Architecture

PhotoEngine is designed to keep compute on the VPS and keep long-term image storage out of it.

- VPS responsibilities: Django, Wagtail, PostgreSQL, Redis, Celery, Gunicorn, Nginx, static files, logs, temporary processing.
- Object storage responsibilities: user-uploaded media in production, including Wagtail uploads and proof gallery previews.
- External delivery responsibilities: final high-resolution client files, delivered through WeTransfer or another external provider.

## Image Storage Strategy

### 1. Static UI assets

- Store design assets in Django static files such as `static/img/`, `static/icons/`, `static/backgrounds/`, `static/theme/`.
- These are deployed through `collectstatic` and served by Nginx.

### 2. Wagtail content images and documents

- Local development: `USE_S3_MEDIA=false` keeps uploads on the local filesystem.
- Production: `USE_S3_MEDIA=true` routes uploads through Django's default storage using `django-storages` and any S3-compatible provider.
- Cloudflare R2 is the recommended target because it is S3-compatible and avoids egress bandwidth charges for repeated proof gallery viewing.

### 3. Proof gallery images

- PhotoEngine currently stores proof gallery images through the existing Wagtail image workflow, which means proof previews follow the configured default Django media storage.
- In production, that keeps proof previews off the VPS as long as `USE_S3_MEDIA=true`.
- Operational guidance for proof previews:
- long edge: 1800-2400 px
- format: WebP or optimized JPEG
- quality: 75-85
- strip metadata when possible
- optional watermarking before upload
- do not upload original final deliverables into the proof gallery

### 4. Final high-resolution deliverables

- Do not store final high-resolution images in PhotoEngine.
- Store only external delivery metadata on the proof gallery:
- provider
- external URL
- expiry date
- access note
- delivery note
- delivery status

## Privacy Modes

### MVP mode

- Hard-to-guess gallery URLs and access tokens.
- Media may be publicly readable from object storage or a public media domain.
- Suitable for staging or lower-sensitivity MVP launches.

### Preferred production mode

- Authenticated client access.
- Private bucket.
- Signed URLs or controlled delivery.
- Recommended for weddings, boudoir, commercial, and other sensitive work.

PhotoEngine does not currently implement signed proof media URLs. Treat that as a future production enhancement.

## Environment Variables

- `DJANGO_SECRET_KEY`: required application secret.
- `DJANGO_ALLOWED_HOSTS`: comma-separated hostnames for Django.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: comma-separated HTTPS origins for admin/forms.
- `DATABASE_URL`: full database connection string used by Django.
- `REDIS_URL`: Redis broker/cache URL used by Celery and cache.
- `USE_S3_MEDIA`: `true` or `false` toggle for uploaded media storage.
- `AWS_*`: generic S3-compatible credentials and endpoint settings. These work with Cloudflare R2 and similar providers.
- `MEDIA_URL`: optional override for public media URL.
- `STATIC_ROOT`: local path where `collectstatic` writes build assets.
- `MEDIA_ROOT`: local filesystem path used when `USE_S3_MEDIA=false`.
- `WAGTAILADMIN_BASE_URL`: absolute base URL used in Wagtail-generated links.

## Local Development

1. Copy `.env.example` to `.env`.
2. Set `DJANGO_SETTINGS_MODULE=PhotoEngine.settings.dev`.
3. Keep `USE_S3_MEDIA=false` unless you explicitly want to test object storage locally.
4. If you are reusing an older Docker Postgres volume, make sure `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` match the credentials that volume was initialized with. If you prefer a clean slate, recreate the Postgres volume.
5. Start the stack:

```sh
docker compose up --build
```

5. Create an admin user if needed:

```sh
docker compose exec web python manage.py createsuperuser
```

## MVP Deployment on Hostinger VPS KVM 2

1. Provision Ubuntu and install Docker Engine plus the Docker Compose plugin.
2. Clone the repository onto the VPS.
3. Copy `.env.example` to `.env` and fill in production values.
4. Point DNS to the VPS.
5. Set `DJANGO_SETTINGS_MODULE=PhotoEngine.settings.production`.
6. Set `USE_S3_MEDIA=true` and fill in your S3-compatible object storage values.
7. Build and start the production stack:

```sh
docker compose -f docker-compose.prod.yml up --build -d
```

8. Run a one-time superuser creation if needed:

```sh
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

9. Configure SSL with Let's Encrypt and add the matching HTTPS server block to `deploy/nginx/default.conf`.
10. Verify:
- Wagtail admin loads
- static files load through Nginx
- Wagtail image uploads work
- proof gallery uploads work
- final delivery links render correctly

## Migration from KVM 2 to Client KVM 4

1. Put the MVP instance into a quiet maintenance window.
2. Back up PostgreSQL.
3. Export or verify the object storage bucket used for media.
4. Provision the client VPS with Docker and Docker Compose.
5. Copy the repository and deployment files.
6. Copy the environment structure, then enter new secrets and domain values on KVM 4.
7. Restore the database.
8. Reconnect either the same bucket or a new object storage bucket.
9. Reissue SSL for the new domain.
10. Verify Wagtail uploads, proof galleries, proof selections, and final external delivery links.

## Backups and Restore

### PostgreSQL

Database backup is critical because it contains gallery structure, client selections, Wagtail content, and external delivery links.

```sh
./scripts/backup_postgres.sh
```

Restore:

```sh
./scripts/restore_postgres.sh backups/photoengine-db-YYYYMMDD-HHMMSS.sql
```

### Object storage

- VPS backups do not protect production media when media is stored in object storage.
- Configure lifecycle rules, versioning, or provider-level backup policy directly on the bucket.
- Keep a documented plan for proof preview retention and cleanup.

### `.env`

- Never commit `.env`.
- Back it up separately in a secure secret-management workflow.

## Operational Guidance

- Keep proof previews optimized before upload.
- Use WeTransfer or another external delivery service for final high-resolution files.
- Monitor VPS disk usage even when media is offloaded, because logs, database growth, and temporary processing still consume space.
- Monitor object storage usage, request counts, and public delivery configuration.
