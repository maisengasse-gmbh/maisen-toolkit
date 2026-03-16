from django.apps import AppConfig


class TotpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "maisen.toolkit.totp"
    label = "maisen_totp"
    verbose_name = "TOTP Two-Factor Authentication"
