from django import forms
from django.core.exceptions import ValidationError


DEFAULT_BULK_UPLOAD_MAX_FILES = 60
DEFAULT_BULK_UPLOAD_MAX_FILE_BYTES = 12 * 1024 * 1024
DEFAULT_BULK_UPLOAD_MAX_TOTAL_BYTES = 200 * 1024 * 1024


def humanize_bytes(num_bytes):
    if num_bytes >= 1024 * 1024:
        value = num_bytes / (1024 * 1024)
        if value.is_integer():
            return f"{int(value)} MB"
        return f"{value:.1f} MB"
    if num_bytes >= 1024:
        value = num_bytes / 1024
        if value.is_integer():
            return f"{int(value)} KB"
        return f"{value:.1f} KB"
    return f"{num_bytes} bytes"


def build_bulk_upload_help_text(base_text, *, max_files=None, max_file_bytes=None, max_total_bytes=None):
    max_files = max_files or DEFAULT_BULK_UPLOAD_MAX_FILES
    max_file_bytes = max_file_bytes or DEFAULT_BULK_UPLOAD_MAX_FILE_BYTES
    max_total_bytes = max_total_bytes or DEFAULT_BULK_UPLOAD_MAX_TOTAL_BYTES
    limit_copy = (
        f" Drag images here or browse files. Upload up to {max_files} images per batch "
        f"({humanize_bytes(max_total_bytes)} total, {humanize_bytes(max_file_bytes)} max per image). "
        "Split larger shoots across multiple saves."
    )
    return f"{base_text}{limit_copy}"


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True
    template_name = "home/widgets/multiple_image_input.html"

    class Media:
        css = {"all": ("css/admin-bulk-upload.css",)}
        js = ("js/admin-bulk-upload.js",)

    def __init__(
        self,
        *args,
        max_files=DEFAULT_BULK_UPLOAD_MAX_FILES,
        max_file_bytes=DEFAULT_BULK_UPLOAD_MAX_FILE_BYTES,
        max_total_bytes=DEFAULT_BULK_UPLOAD_MAX_TOTAL_BYTES,
        dropzone_title="Drag and drop images here",
        dropzone_hint="or click to browse",
        **kwargs,
    ):
        attrs = kwargs.setdefault("attrs", {})
        attrs["class"] = f"{attrs.get('class', '')} bulk-upload-widget__input".strip()
        attrs.setdefault("accept", "image/*")
        attrs["data-max-files"] = str(max_files)
        attrs["data-max-file-bytes"] = str(max_file_bytes)
        attrs["data-max-total-bytes"] = str(max_total_bytes)
        attrs["data-dropzone-title"] = dropzone_title
        attrs["data-dropzone-hint"] = dropzone_hint
        attrs["multiple"] = True
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        widget_attrs = context["widget"]["attrs"]
        max_files = int(widget_attrs["data-max-files"])
        max_file_bytes = int(widget_attrs["data-max-file-bytes"])
        max_total_bytes = int(widget_attrs["data-max-total-bytes"])
        context["widget"]["bulk_upload"] = {
            "dropzone_title": widget_attrs["data-dropzone-title"],
            "dropzone_hint": widget_attrs["data-dropzone-hint"],
            "max_files": max_files,
            "max_file_label": humanize_bytes(max_file_bytes),
            "max_total_label": humanize_bytes(max_total_bytes),
        }
        return context


class MultipleImageFileField(forms.FileField):
    widget = MultipleImageInput

    def __init__(
        self,
        *args,
        max_files=DEFAULT_BULK_UPLOAD_MAX_FILES,
        max_file_bytes=DEFAULT_BULK_UPLOAD_MAX_FILE_BYTES,
        max_total_bytes=DEFAULT_BULK_UPLOAD_MAX_TOTAL_BYTES,
        dropzone_title="Drag and drop images here",
        dropzone_hint="or click to browse",
        **kwargs,
    ):
        widget = kwargs.pop("widget", None) or self.widget(
            max_files=max_files,
            max_file_bytes=max_file_bytes,
            max_total_bytes=max_total_bytes,
            dropzone_title=dropzone_title,
            dropzone_hint=dropzone_hint,
        )
        self.max_files = max_files
        self.max_file_bytes = max_file_bytes
        self.max_total_bytes = max_total_bytes
        super().__init__(*args, widget=widget, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        if len(data) > self.max_files:
            raise ValidationError(
                f"Upload up to {self.max_files} images per batch. Split larger uploads into multiple saves."
            )

        cleaned_files = []
        total_bytes = 0

        for item in data:
            cleaned_item = single_file_clean(item, initial)
            file_size = getattr(cleaned_item, "size", 0) or 0

            if file_size > self.max_file_bytes:
                raise ValidationError(
                    f"{cleaned_item.name} is {humanize_bytes(file_size)}. Keep each image under {humanize_bytes(self.max_file_bytes)}."
                )

            cleaned_files.append(cleaned_item)
            total_bytes += file_size

        if total_bytes > self.max_total_bytes:
            raise ValidationError(
                f"This batch totals {humanize_bytes(total_bytes)}. Keep each upload under {humanize_bytes(self.max_total_bytes)}."
            )

        return cleaned_files
