import base64
import json

from django.contrib import admin, messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from fido2 import cbor
from fido2.webauthn import AttestedCredentialData

from maisen.toolkit.conf import get_passkey_setting
from maisen.toolkit.passkeys.forms import PasskeyNameForm
from maisen.toolkit.passkeys.signals import (
    passkey_deleted,
    passkey_registered,
    passkey_verified,
)
from maisen.toolkit.passkeys.utils import (
    get_credential_model,
    get_fido2_server,
    get_user_credentials,
)


def _build_context(request, extra=None, is_admin=False):
    """Baut den Kontext auf – für Admin inkl. Unfold-Sidebar/Header."""
    ctx = {}
    if is_admin:
        ctx.update(admin.site.each_context(request))
    if extra:
        ctx.update(extra)
    return ctx


def _b64url_encode(data):
    """Base64url-Encoding ohne Padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s):
    """Base64url-Decoding mit Padding-Korrektur."""
    s += "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)


def _serialize_options(obj):
    """Serialisiert fido2-Objekte rekursiv zu JSON-kompatiblen Dicts."""
    if isinstance(obj, bytes):
        return _b64url_encode(obj)
    if isinstance(obj, dict):
        return {k: _serialize_options(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize_options(v) for v in obj]
    return obj


# ---------------------------------------------------------------------------
# HTML-Views
# ---------------------------------------------------------------------------


def passkey_verify(
    request,
    template_name,
    success_url="/",
    is_admin=False,
    **kwargs,
):
    """Passkey-Verifizierung nach Login."""
    CredentialModel = get_credential_model()
    has_credentials = CredentialModel.objects.filter(user=request.user).exists()

    if not has_credentials:
        messages.error(
            request, _("Kein Passkey für diesen Account registriert.")
        )

    ctx = _build_context(
        request,
        {
            "title": _("Passkey-Verifizierung"),
            "success_url": success_url,
            "has_credentials": has_credentials,
        },
        is_admin=is_admin,
    )
    return render(request, template_name, ctx)


def passkey_manage(
    request,
    template_name,
    manage_url_name="passkeys:manage",
    is_admin=False,
    form_class=None,
    **kwargs,
):
    """Passkey-Selbstverwaltung: registrieren und löschen."""
    if form_class is None:
        form_class = PasskeyNameForm
    CredentialModel = get_credential_model()

    if request.method == "POST":
        action = request.POST.get("action")
        user = request.user

        if action == "delete":
            credential_id = request.POST.get("credential_id")
            if credential_id:
                deleted, _detail = CredentialModel.objects.filter(
                    user=user, pk=credential_id
                ).delete()
                if deleted:
                    passkey_deleted.send(
                        sender=user.__class__, user=user, request=request
                    )
                    messages.success(request, _("Passkey wurde gelöscht."))
                else:
                    messages.error(request, _("Passkey nicht gefunden."))
            return redirect(manage_url_name)

    credentials = CredentialModel.objects.filter(user=request.user)
    form = form_class()

    ctx = _build_context(
        request,
        {
            "form": form,
            "credentials": credentials,
            "title": _("Passkeys verwalten"),
        },
        is_admin=is_admin,
    )
    return render(request, template_name, ctx)


# ---------------------------------------------------------------------------
# JSON-Endpoints (WebAuthn-Zeremonie) — fido2 >= 2.0 API
# ---------------------------------------------------------------------------


@require_POST
def passkey_register_begin(request):
    """Startet die Passkey-Registrierung (Attestation)."""
    server = get_fido2_server()
    credentials = get_user_credentials(request.user)

    registration_data, state = server.register_begin(
        {
            "id": str(request.user.pk).encode(),
            "name": request.user.get_username(),
            "displayName": request.user.get_full_name()
            or request.user.get_username(),
        },
        credentials,
        resident_key_requirement="preferred",
        user_verification="preferred",
    )

    request.session["passkey_register_state"] = state

    # Name aus POST-Body speichern
    try:
        body = json.loads(request.body)
        name = body.get("name", "")
    except (json.JSONDecodeError, ValueError):
        name = ""
    request.session["passkey_register_name"] = name

    # Options serialisieren (bytes → base64url)
    return JsonResponse(_serialize_options(dict(registration_data)))


@require_POST
def passkey_register_complete(request):
    """Beendet die Passkey-Registrierung (Attestation)."""
    server = get_fido2_server()
    state = request.session.pop("passkey_register_state", None)
    name = request.session.pop("passkey_register_name", _("Passkey"))

    if not state:
        return JsonResponse(
            {"error": "Keine aktive Registrierung."}, status=400
        )

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Ungültiger Request."}, status=400)

    try:
        auth_data = server.register_complete(state, body)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    cred_data = auth_data.credential_data

    CredentialModel = get_credential_model()
    credential = CredentialModel.objects.create(
        user=request.user,
        name=name or _("Passkey"),
        credential_id=cred_data.credential_id,
        public_key=cbor.encode(cred_data.public_key),
        sign_count=auth_data.counter,
        aaguid=str(cred_data.aaguid) if cred_data.aaguid else "",
    )

    request.session["passkey_verified"] = True

    passkey_registered.send(
        sender=request.user.__class__,
        user=request.user,
        request=request,
        credential=credential,
    )

    return JsonResponse({"status": "ok"})


@require_POST
def passkey_authenticate_begin(request):
    """Startet die Passkey-Authentifizierung (Assertion)."""
    server = get_fido2_server()
    credentials = get_user_credentials(request.user)

    if not credentials:
        return JsonResponse(
            {"error": "Kein Passkey registriert."}, status=400
        )

    assertion_data, state = server.authenticate_begin(
        credentials,
        user_verification="preferred",
    )

    request.session["passkey_auth_state"] = state

    # Options serialisieren (bytes → base64url)
    return JsonResponse(_serialize_options(dict(assertion_data)))


@require_POST
def passkey_authenticate_complete(request):
    """Beendet die Passkey-Authentifizierung (Assertion)."""
    server = get_fido2_server()
    state = request.session.pop("passkey_auth_state", None)

    if not state:
        return JsonResponse(
            {"error": "Keine aktive Authentifizierung."}, status=400
        )

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Ungültiger Request."}, status=400)

    credentials = get_user_credentials(request.user)

    # fido2 2.x API: authenticate_complete(state, credentials, response_dict)
    try:
        server.authenticate_complete(state, credentials, body)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=400)

    # Sign-Count und last_used_at aktualisieren
    try:
        credential_id = _b64url_decode(body["rawId"])
        CredentialModel = get_credential_model()
        db_cred = CredentialModel.objects.filter(
            user=request.user,
            credential_id=credential_id,
        ).first()
        if db_cred:
            db_cred.last_used_at = timezone.now()
            db_cred.save(update_fields=["last_used_at"])
    except (KeyError, Exception):
        pass  # Sign-Count-Update ist optional

    request.session["passkey_verified"] = True

    passkey_verified.send(
        sender=request.user.__class__,
        user=request.user,
        request=request,
    )

    return JsonResponse({"status": "ok"})
