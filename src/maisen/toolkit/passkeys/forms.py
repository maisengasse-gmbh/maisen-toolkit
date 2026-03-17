from django import forms
from django.utils.translation import gettext_lazy as _


class PasskeyNameForm(forms.Form):
    """Formular für die Benennung eines neuen Passkeys."""

    name = forms.CharField(
        label=_("Passkey-Name"),
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": _("z.\u202fB. MacBook Touch ID"),
            }
        ),
    )


try:
    from unfold.widgets import UnfoldAdminTextInputWidget

    class UnfoldPasskeyNameForm(PasskeyNameForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["name"].widget = UnfoldAdminTextInputWidget(
                attrs={
                    "autofocus": True,
                    "placeholder": _("z.\u202fB. MacBook Touch ID"),
                }
            )

except ImportError:
    pass  # Unfold nicht installiert
