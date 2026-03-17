from django.shortcuts import redirect
from django.urls import reverse

from maisen.toolkit.conf import get_passkey_setting
from maisen.toolkit.passkeys.utils import user_requires_passkey


class PasskeyMiddleware:
    """
    Erzwingt Passkey-Verifikation im Django Admin und optional im Frontend.

    Konfiguration via MAISEN_PASSKEYS in den Django-Settings:
      ADMIN_ONLY: True  → nur /admin/ schützen (Default)
      ADMIN_ONLY: False → auch Frontend schützen
      ACCEPT_TOTP_VERIFIED: True → akzeptiert auch TOTP-Verifikation
      ADMIN_VERIFY_URL_NAME / ADMIN_SETUP_URL_NAME: URL-Namen für Redirects
      FRONTEND_VERIFY_URL_NAME / FRONTEND_SETUP_URL_NAME: URL-Namen für Redirects
      ADMIN_EXEMPT_PREFIXES: Pfade im Admin, die ohne Passkey erreichbar sind
      EXEMPT_URL_PREFIXES: Frontend-Pfade, die ohne Passkey erreichbar sind
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated or not user_requires_passkey(
            request.user
        ):
            return self.get_response(request)

        verified = request.session.get("passkey_verified")
        # Optional auch TOTP-Verifikation akzeptieren
        if not verified and get_passkey_setting("ACCEPT_TOTP_VERIFIED"):
            verified = request.session.get("totp_verified")

        # Admin-Bereich
        if request.path.startswith("/admin/"):
            admin_verify = reverse(get_passkey_setting("ADMIN_VERIFY_URL_NAME"))
            admin_manage = reverse(get_passkey_setting("ADMIN_MANAGE_URL_NAME"))
            admin_exempt = get_passkey_setting("ADMIN_EXEMPT_PREFIXES")

            # Passkey-eigene URLs und exempt Pfade durchlassen
            if any(
                request.path.startswith(p)
                for p in (admin_verify, admin_manage, *admin_exempt)
            ):
                return self.get_response(request)

            if request.user.has_passkeys:
                if not verified:
                    return redirect(admin_verify)
            else:
                # Kein Passkey registriert → zur Manage-Seite zum Einrichten
                return redirect(admin_manage)

        # Frontend-Bereich (nur wenn nicht ADMIN_ONLY)
        admin_only = get_passkey_setting("ADMIN_ONLY")
        if not admin_only:
            frontend_verify = reverse(
                get_passkey_setting("FRONTEND_VERIFY_URL_NAME")
            )
            frontend_manage = reverse(
                get_passkey_setting("FRONTEND_SETUP_URL_NAME")
            )
            exempt = get_passkey_setting("EXEMPT_URL_PREFIXES")
            # /admin/ ist immer exempt (wird oben behandelt)
            all_exempt = (
                *tuple(exempt),
                "/admin/",
                frontend_verify,
                frontend_manage,
            )

            if not any(request.path.startswith(p) for p in all_exempt):
                if request.user.has_passkeys:
                    if not verified:
                        return redirect(frontend_verify)
                else:
                    return redirect(frontend_manage)

        return self.get_response(request)
