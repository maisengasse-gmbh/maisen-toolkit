from django import forms
from django.utils.translation import gettext_lazy as _


class TotpCodeForm(forms.Form):
    """Formular für die Eingabe eines 6-stelligen TOTP-Codes."""

    code = forms.CharField(
        label=_("Authentifizierungscode"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
                "autofocus": True,
                "placeholder": "000000",
            }
        ),
    )
