import pyotp
from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from maisen.toolkit.conf import get_totp_setting
from maisen.toolkit.totp.forms import TotpCodeForm
from maisen.toolkit.totp.utils import render_qr


def _build_context(request, extra=None, is_admin=False):
    """Baut den Kontext auf – für Admin inkl. Unfold-Sidebar/Header."""
    ctx = {}
    if is_admin:
        ctx.update(admin.site.each_context(request))
    if extra:
        ctx.update(extra)
    return ctx


def totp_verify(
    request,
    template_name,
    success_url="/",
    setup_url_name="totp:setup",
    is_admin=False,
):
    """TOTP-Code-Eingabe nach Login."""
    form = TotpCodeForm(request.POST or None)
    valid_window = get_totp_setting("VERIFY_VALID_WINDOW")

    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"]
        user = request.user

        if not user.totp_secret or not user.totp_enabled:
            messages.error(request, _("2FA ist für diesen Account nicht eingerichtet."))
            return redirect(setup_url_name)

        if pyotp.TOTP(user.totp_secret).verify(code, valid_window=valid_window):
            request.session["totp_verified"] = True
            request.session.pop("totp_setup_forced", None)
            return redirect(success_url)

        messages.error(request, _("Ungültiger Code. Bitte erneut versuchen."))

    ctx = _build_context(
        request,
        {
            "form": form,
            "title": _("2FA-Verifikation"),
            "is_popup": request.session.get("totp_setup_forced", False),
        },
        is_admin=is_admin,
    )
    return render(request, template_name, ctx)


def totp_setup(
    request,
    template_name,
    manage_url_name="totp:manage",
    is_admin=False,
):
    """TOTP-Setup: QR-Code anzeigen und Code bestätigen."""
    session_key = "totp_setup_secret"
    valid_window = get_totp_setting("SETUP_VALID_WINDOW")
    form = TotpCodeForm(request.POST or None)

    secret = request.session.get(session_key)
    if not secret:
        secret = pyotp.random_base32()
        request.session[session_key] = secret

    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"]

        if not secret:
            messages.error(request, _("Setup-Session abgelaufen. Bitte neu starten."))
            return render(
                request,
                template_name,
                _build_context(
                    request,
                    {
                        "form": TotpCodeForm(),
                        "qr_code": render_qr(secret, request.user.username),
                        "secret": secret,
                        "title": _("2FA einrichten"),
                        "is_popup": request.session.get("totp_setup_forced", False),
                    },
                    is_admin=is_admin,
                ),
            )

        if pyotp.TOTP(secret).verify(code, valid_window=valid_window):
            user = request.user
            user.totp_secret = secret
            user.totp_enabled = True
            user.save(update_fields=["totp_secret", "totp_enabled"])
            del request.session[session_key]
            request.session["totp_verified"] = True
            request.session.pop("totp_setup_forced", None)
            messages.success(request, _("2FA erfolgreich eingerichtet."))
            return redirect(manage_url_name)

        messages.error(request, _("Ungültiger Code. Bitte erneut versuchen."))

    ctx = _build_context(
        request,
        {
            "form": form,
            "qr_code": render_qr(secret, request.user.username),
            "secret": secret,
            "title": _("2FA einrichten"),
            "is_popup": request.session.get("totp_setup_forced", False),
        },
        is_admin=is_admin,
    )
    return render(request, template_name, ctx)


def totp_manage(
    request,
    template_name,
    manage_url_name="totp:manage",
    setup_url_name="totp:setup",
    is_admin=False,
):
    """TOTP-Selbstverwaltung: deaktivieren oder neu einrichten."""
    valid_window = get_totp_setting("VERIFY_VALID_WINDOW")
    form = TotpCodeForm(request.POST or None)

    if request.method == "POST":
        action = request.POST.get("action")
        user = request.user

        if action == "disable" and form.is_valid():
            code = form.cleaned_data["code"]
            if not user.totp_enabled:
                messages.error(request, _("2FA ist nicht aktiv."))
            elif not pyotp.TOTP(user.totp_secret).verify(
                code, valid_window=valid_window
            ):
                messages.error(
                    request, _("Ungültiger Code. Bitte erneut versuchen.")
                )
            else:
                user.totp_secret = ""
                user.totp_enabled = False
                user.save(update_fields=["totp_secret", "totp_enabled"])
                request.session.pop("totp_verified", None)
                messages.success(request, _("2FA wurde deaktiviert."))
                return redirect(manage_url_name)

    ctx = _build_context(
        request,
        {
            "form": form,
            "setup_url_name": setup_url_name,
            "title": _("2FA verwalten"),
        },
        is_admin=is_admin,
    )
    return render(request, template_name, ctx)
