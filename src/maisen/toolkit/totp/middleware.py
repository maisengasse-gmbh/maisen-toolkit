from django.shortcuts import redirect
from django.urls import reverse

from maisen.toolkit.conf import get_totp_setting
from maisen.toolkit.totp.utils import user_requires_totp


class TotpMiddleware:
    """
    Erzwingt TOTP-Verifikation im Django Admin und optional im Frontend.

    Akzeptiert neben session["totp_verified"] auch session["passkey_verified"]
    als gültige Verifikation (konfigurierbar via ACCEPT_PASSKEY_VERIFIED).

    Konfiguration via MAISEN_TOTP in den Django-Settings:
      ADMIN_ONLY: True  → nur /admin/ schützen (Default)
      ADMIN_ONLY: False → auch Frontend schützen
      ACCEPT_PASSKEY_VERIFIED: True → akzeptiert auch Passkey-Verifikation
      ADMIN_VERIFY_URL_NAME / ADMIN_SETUP_URL_NAME: URL-Namen für Redirects
      FRONTEND_VERIFY_URL_NAME / FRONTEND_SETUP_URL_NAME: URL-Namen für Redirects
      ADMIN_EXEMPT_PREFIXES: Pfade im Admin, die ohne TOTP erreichbar sind
      EXEMPT_URL_PREFIXES: Frontend-Pfade, die ohne TOTP erreichbar sind
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated or not user_requires_totp(request.user):
            return self.get_response(request)

        verified = request.session.get("totp_verified")
        # Optional auch Passkey-Verifikation akzeptieren
        accept_passkey = get_totp_setting("ACCEPT_PASSKEY_VERIFIED")
        if not verified and accept_passkey:
            verified = request.session.get("passkey_verified")

        # User hat Passkeys → kein TOTP-Setup erzwingen
        has_passkeys = accept_passkey and getattr(request.user, "has_passkeys", False)

        # Admin-Bereich
        if request.path.startswith("/admin/"):
            admin_verify = reverse(get_totp_setting("ADMIN_VERIFY_URL_NAME"))
            admin_setup = reverse(get_totp_setting("ADMIN_SETUP_URL_NAME"))
            admin_manage = reverse(get_totp_setting("ADMIN_MANAGE_URL_NAME"))
            admin_exempt = get_totp_setting("ADMIN_EXEMPT_PREFIXES")

            # TOTP-eigene URLs und exempt Pfade durchlassen
            if any(
                request.path.startswith(p)
                for p in (admin_verify, admin_setup, admin_manage, *admin_exempt)
            ):
                return self.get_response(request)

            if request.user.totp_enabled:
                if not verified:
                    request.session["totp_setup_forced"] = True
                    return redirect(admin_verify)
            elif has_passkeys:
                # Passkeys vorhanden → Verify statt Setup
                if not verified:
                    request.session["totp_setup_forced"] = True
                    return redirect(admin_verify)
            else:
                request.session["totp_setup_forced"] = True
                return redirect(admin_setup)

        # Frontend-Bereich (nur wenn nicht ADMIN_ONLY)
        admin_only = get_totp_setting("ADMIN_ONLY")
        if not admin_only:
            frontend_verify = reverse(get_totp_setting("FRONTEND_VERIFY_URL_NAME"))
            frontend_setup = reverse(get_totp_setting("FRONTEND_SETUP_URL_NAME"))
            exempt = get_totp_setting("EXEMPT_URL_PREFIXES")
            # /admin/ ist immer exempt (wird oben behandelt)
            all_exempt = (*tuple(exempt), "/admin/", frontend_verify, frontend_setup)

            if not any(request.path.startswith(p) for p in all_exempt):
                if request.user.totp_enabled:
                    if not verified:
                        return redirect(frontend_verify)
                elif has_passkeys:
                    if not verified:
                        return redirect(frontend_verify)
                else:
                    return redirect(frontend_setup)

        return self.get_response(request)
