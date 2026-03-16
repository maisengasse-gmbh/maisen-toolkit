from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from maisen.toolkit.totp.utils import user_requires_totp


class TotpUserAdminMixin:
    """
    Mixin für den UserAdmin – fügt TOTP-Fieldset, Display und Actions hinzu.

    Verwendung:
        class AccountAdmin(TotpUserAdminMixin, UserAdmin, UnfoldAdmin):
            fieldsets = UserAdmin.fieldsets + TotpUserAdminMixin.totp_fieldset
            readonly_fields = TotpUserAdminMixin.totp_readonly_fields
            actions = ["reset_totp"]
    """

    totp_fieldset = (
        (
            _("Zwei-Faktor-Authentifizierung"),
            {
                "fields": ("totp_enabled", "totp_required_display"),
                "classes": ["tab"],
            },
        ),
    )

    totp_readonly_fields = ("totp_enabled", "totp_required_display")

    @admin.display(description=_("TOTP-Pflicht (via Gruppe/Superuser)"), boolean=True)
    def totp_required_display(self, obj):
        return user_requires_totp(obj)

    @admin.action(description=_("TOTP zurücksetzen"))
    def reset_totp(self, request, queryset):
        queryset.update(totp_secret="", totp_enabled=False)
        self.message_user(
            request, _("TOTP wurde für die ausgewählten Benutzer zurückgesetzt.")
        )
