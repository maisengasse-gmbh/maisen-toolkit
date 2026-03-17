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
    # URL-Namen für Middleware-Redirects (müssen zu den eingebundenen Patterns passen)
    "ADMIN_VERIFY_URL_NAME": "admin_totp:verify",
    "ADMIN_SETUP_URL_NAME": "admin_totp:setup",
    "ADMIN_MANAGE_URL_NAME": "admin_totp:manage",
    "FRONTEND_VERIFY_URL_NAME": "totp:verify",
    "FRONTEND_SETUP_URL_NAME": "totp:setup",
    # Admin-Pfade, die ohne TOTP erreichbar sein müssen
    "ADMIN_EXEMPT_PREFIXES": ("/admin/login", "/admin/logout", "/admin/jsi18n"),
}


def get_totp_setting(name):
    """Liest ein TOTP-Setting aus MAISEN_TOTP oder gibt den Default zurück."""
    user_settings = getattr(settings, "MAISEN_TOTP", {})
    return user_settings.get(name, DEFAULTS[name])


# ---------------------------------------------------------------------------
# Passkey (WebAuthn) Settings
# ---------------------------------------------------------------------------

PASSKEYS_DEFAULTS = {
    "RP_ID": "localhost",
    "RP_NAME": "Django App",
    "ORIGIN": "http://localhost:8000",
    "TIMEOUT": 60000,
    # Pflicht! z.B. "accounts.PasskeyCredential"
    "CREDENTIAL_MODEL": None,
    # Akzeptiert auch TOTP-Verifikation in der Passkey-Middleware
    "ACCEPT_TOTP_VERIFIED": True,
    "ADMIN_ONLY": True,
    "EXEMPT_URL_PREFIXES": (
        "/login/",
        "/logout/",
        "/static/",
        "/media/",
        "/api/",
    ),
    "ADMIN_VERIFY_URL_NAME": "admin_passkeys:verify",
    "ADMIN_SETUP_URL_NAME": "admin_passkeys:manage",
    "ADMIN_MANAGE_URL_NAME": "admin_passkeys:manage",
    "FRONTEND_VERIFY_URL_NAME": "passkeys:verify",
    "FRONTEND_SETUP_URL_NAME": "passkeys:manage",
    "ADMIN_EXEMPT_PREFIXES": ("/admin/login", "/admin/logout", "/admin/jsi18n"),
}


def get_passkey_setting(name):
    """Liest ein Passkey-Setting aus MAISEN_PASSKEYS oder gibt den Default zurück."""
    user_settings = getattr(settings, "MAISEN_PASSKEYS", {})
    return user_settings.get(name, PASSKEYS_DEFAULTS[name])
