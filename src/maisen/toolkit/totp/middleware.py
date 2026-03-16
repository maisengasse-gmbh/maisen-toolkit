from django.shortcuts import redirect

from maisen.toolkit.conf import get_totp_setting
from maisen.toolkit.totp.utils import user_requires_totp


class TotpMiddleware:
    """
    Erzwingt TOTP-Verifikation im Django Admin und optional im Frontend.

    Konfiguration via MAISEN_TOTP in den Django-Settings:
      ADMIN_ONLY: True  → nur /admin/ schützen (Default)
      ADMIN_ONLY: False → auch Frontend schützen
      EXEMPT_URL_PREFIXES: Tuple von Pfaden, die ohne TOTP erreichbar sind
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated or not user_requires_totp(request.user):
            return self.get_response(request)

        verified = request.session.get("totp_verified")

        # Admin-Bereich
        if (
            request.path.startswith("/admin/")
            and not request.path.startswith("/admin/totp/")
            and not request.path.startswith("/admin/login")
            and not request.path.startswith("/admin/logout")
            and not request.path.startswith("/admin/jsi18n")
        ):
            if request.user.totp_enabled:
                if not verified:
                    request.session["totp_setup_forced"] = True
                    return redirect("/admin/totp/verify/")
            else:
                request.session["totp_setup_forced"] = True
                return redirect("/admin/totp/setup/")

        # Frontend-Bereich (nur wenn nicht ADMIN_ONLY)
        admin_only = get_totp_setting("ADMIN_ONLY")
        if not admin_only:
            exempt = get_totp_setting("EXEMPT_URL_PREFIXES")
            # /admin/ ist immer exempt (wird oben behandelt)
            all_exempt = tuple(exempt) + ("/admin/",)

            if not any(request.path.startswith(p) for p in all_exempt):
                if request.user.totp_enabled:
                    if not verified:
                        return redirect("/totp/verify/")
                else:
                    return redirect("/totp/setup/")

        return self.get_response(request)
