from django import forms

from home.i18n import choose_translation
from home.models import ContactPage


class ContactInquiryForm(forms.Form):
    PHOTOGRAPHY_TYPE_CHOICES = [
        (ContactPage.PHOTOGRAPHY_TYPE_WEDDING, "Wedding"),
        (ContactPage.PHOTOGRAPHY_TYPE_ENGAGEMENT, "Engagement"),
        (ContactPage.PHOTOGRAPHY_TYPE_PORTRAIT, "Portrait"),
        (ContactPage.PHOTOGRAPHY_TYPE_FAMILY, "Family"),
        (ContactPage.PHOTOGRAPHY_TYPE_EVENT, "Event"),
        (ContactPage.PHOTOGRAPHY_TYPE_BRAND, "Brand"),
        (ContactPage.PHOTOGRAPHY_TYPE_OTHER, "Other"),
    ]

    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=40)
    photography_type = forms.ChoiceField(choices=PHOTOGRAPHY_TYPE_CHOICES)
    desired_start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    desired_end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}))

    def __init__(self, *args, language_code=None, **kwargs):
        super().__init__(*args, **kwargs)
        language_code = language_code or "en"
        self.fields["name"].label = choose_translation(
            en="Name",
            fr="Nom",
            language_code=language_code,
        )
        self.fields["email"].label = choose_translation(
            en="Email",
            fr="Courriel",
            language_code=language_code,
        )
        self.fields["phone_number"].label = choose_translation(
            en="Phone Number",
            fr="Numero de telephone",
            language_code=language_code,
        )
        self.fields["photography_type"].label = choose_translation(
            en="Type of Photography Requested",
            fr="Type de photographie demande",
            language_code=language_code,
        )
        self.fields["desired_start_date"].label = choose_translation(
            en="Preferred Start Date",
            fr="Date de debut souhaitee",
            language_code=language_code,
        )
        self.fields["desired_end_date"].label = choose_translation(
            en="Preferred End Date",
            fr="Date de fin souhaitee",
            language_code=language_code,
        )
        self.fields["message"].label = choose_translation(
            en="Message",
            fr="Message",
            language_code=language_code,
        )
        self.fields["photography_type"].choices = [
            (
                ContactPage.PHOTOGRAPHY_TYPE_WEDDING,
                choose_translation(en="Wedding", fr="Mariage", language_code=language_code),
            ),
            (
                ContactPage.PHOTOGRAPHY_TYPE_ENGAGEMENT,
                choose_translation(en="Engagement", fr="Fiancailles", language_code=language_code),
            ),
            (
                ContactPage.PHOTOGRAPHY_TYPE_PORTRAIT,
                choose_translation(en="Portrait", fr="Portrait", language_code=language_code),
            ),
            (
                ContactPage.PHOTOGRAPHY_TYPE_FAMILY,
                choose_translation(en="Family", fr="Famille", language_code=language_code),
            ),
            (
                ContactPage.PHOTOGRAPHY_TYPE_EVENT,
                choose_translation(en="Event", fr="Evenement", language_code=language_code),
            ),
            (
                ContactPage.PHOTOGRAPHY_TYPE_BRAND,
                choose_translation(en="Brand", fr="Marque", language_code=language_code),
            ),
            (
                ContactPage.PHOTOGRAPHY_TYPE_OTHER,
                choose_translation(en="Other", fr="Autre", language_code=language_code),
            ),
        ]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("desired_start_date")
        end_date = cleaned_data.get("desired_end_date")

        if start_date and end_date and end_date < start_date:
            self.add_error(
                "desired_end_date",
                choose_translation(
                    en="The end date must be on or after the start date.",
                    fr="La date de fin doit etre egale ou posterieure a la date de debut.",
                ),
            )

        return cleaned_data
