from django.conf import settings

DEFAULTS = {
    "ISSUER": "Django App",
    "VERIFY_VALID_WINDOW": 1,
    "SETUP_VALID_WINDOW": 2,
    "ADMIN_ONLY": True,
    "EXEMPT_URL_PREFIXES": (
        "/login/",
        "/logout/",
        "/static/",
        "/media/",
        "/api/",
    ),
}


def get_totp_setting(name):
    """Liest ein TOTP-Setting aus MAISEN_TOTP oder gibt den Default zurück."""
    user_settings = getattr(settings, "MAISEN_TOTP", {})
    return user_settings.get(name, DEFAULTS[name])
