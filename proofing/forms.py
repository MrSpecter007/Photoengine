from django import forms

from home.i18n import choose_translation


class ProofingPortalAccessForm(forms.Form):
    access_token = forms.CharField(
        label="Access token",
        max_length=64,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Paste your proofing access token",
                "autocomplete": "off",
                "spellcheck": "false",
            }
        ),
    )

    def __init__(self, *args, language_code=None, **kwargs):
        super().__init__(*args, **kwargs)
        language_code = language_code or "en"
        self.fields["access_token"].label = choose_translation(
            en="Access token",
            fr="Jeton d'acces",
            language_code=language_code,
        )
        self.fields["access_token"].widget.attrs["placeholder"] = choose_translation(
            en="Paste your proofing access token",
            fr="Collez votre jeton d'acces a la galerie",
            language_code=language_code,
        )
