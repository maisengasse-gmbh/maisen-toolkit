from django.apps import AppConfig


class PasskeysConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "maisen.toolkit.passkeys"
    label = "maisen_passkeys"
    verbose_name = "Passkey (WebAuthn) Authentication"
