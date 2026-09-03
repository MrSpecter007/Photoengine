from whitenoise.storage import CompressedManifestStaticFilesStorage


class RelaxedCompressedManifestStorage(CompressedManifestStaticFilesStorage):
    """Like CompressedManifestStaticFilesStorage but falls back to the plain URL
    when a file is missing from the manifest instead of raising ValueError.
    This prevents template crashes when a static file is referenced in a template
    but not present on disk (e.g. legacy theme files not committed to git)."""

    def url(self, name, force=False):
        try:
            return super().url(name, force)
        except ValueError:
            return self._base_url + name
