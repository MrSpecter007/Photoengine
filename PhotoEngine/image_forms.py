from pathlib import Path

from wagtail.images.forms import BaseImageForm


class AutoTitleImageForm(BaseImageForm):
    """
    Allow chooser uploads to succeed even when the title input is left blank.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "title" in self.fields:
            self.fields["title"].required = False

    def clean(self):
        cleaned_data = super().clean()
        title = (cleaned_data.get("title") or "").strip()
        uploaded_file = cleaned_data.get("file") or getattr(self.instance, "file", None)

        if not title and uploaded_file:
            cleaned_data["title"] = Path(uploaded_file.name).stem

        return cleaned_data
