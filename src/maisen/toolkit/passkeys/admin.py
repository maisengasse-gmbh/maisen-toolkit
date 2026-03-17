from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from maisen.toolkit.passkeys.utils import get_credential_model


class PasskeyUserAdminMixin:
    """
    Mixin für den UserAdmin – fügt Passkey-Fieldset, Display und Actions hinzu.

    Verwendung:
        class AccountAdmin(PasskeyUserAdminMixin, UserAdmin, UnfoldAdmin):
            fieldsets = UserAdmin.fieldsets + PasskeyUserAdminMixin.passkey_fieldset
            readonly_fields = PasskeyUserAdminMixin.passkey_readonly_fields
            actions = ["reset_passkeys"]
    """

    passkey_fieldset = (
        (
            _("Passkeys (WebAuthn)"),
            {
                "fields": ("passkey_count_display",),
                "classes": ["tab"],
            },
        ),
    )

    passkey_readonly_fields = ("passkey_count_display",)

    @admin.display(description=_("Registrierte Passkeys"))
    def passkey_count_display(self, obj):
        CredentialModel = get_credential_model()
        return CredentialModel.objects.filter(user=obj).count()

    @admin.action(description=_("Passkeys zurücksetzen"))
    def reset_passkeys(self, request, queryset):
        CredentialModel = get_credential_model()
        for user in queryset:
            CredentialModel.objects.filter(user=user).delete()
        self.message_user(
            request,
            _("Passkeys wurden für die ausgewählten Benutzer zurückgesetzt."),
        )
