from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from maisen.toolkit.passkeys.utils import get_credential_model, user_requires_passkey


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
                "fields": ("passkey_count_display", "passkey_required_display"),
                "classes": ["tab"],
            },
        ),
    )

    passkey_readonly_fields = ("passkey_count_display", "passkey_required_display")

    @admin.display(description=_("Registrierte Passkeys"))
    def passkey_count_display(self, obj):
        CredentialModel = get_credential_model()
        return CredentialModel.objects.filter(user=obj).count()

    @admin.display(
        description=_("Passkey-Pflicht (via Gruppe/Superuser)"), boolean=True
    )
    def passkey_required_display(self, obj):
        return user_requires_passkey(obj)

    @admin.action(description=_("Passkeys zurücksetzen"))
    def reset_passkeys(self, request, queryset):
        CredentialModel = get_credential_model()
        for user in queryset:
            CredentialModel.objects.filter(user=user).delete()
        self.message_user(
            request,
            _("Passkeys wurden für die ausgewählten Benutzer zurückgesetzt."),
        )
