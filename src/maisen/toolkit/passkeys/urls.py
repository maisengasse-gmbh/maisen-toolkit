"""
Standard-URL-Patterns für Passkeys (Admin + Frontend).

Verwendung in urls.py des Projekts:

    from maisen.toolkit.passkeys.urls import admin_urlpatterns, frontend_urlpatterns

    urlpatterns = [
        path("admin/passkeys/", include((admin_urlpatterns, "passkeys"), namespace="admin_passkeys")),
        path("passkeys/", include((frontend_urlpatterns, "passkeys"), namespace="passkeys")),
        ...
    ]

Für Unfold-Admin-Templates stattdessen urls_unfold verwenden:

    from maisen.toolkit.passkeys.urls_unfold import admin_urlpatterns
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.urls import path

from maisen.toolkit.passkeys import views

app_name = "passkeys"

# ---------------------------------------------------------------------------
# Admin-Passkey-URLs (basic Templates)
# ---------------------------------------------------------------------------
admin_urlpatterns = [
    path(
        "verify/",
        staff_member_required(views.passkey_verify),
        {
            "template_name": "maisen_passkeys/verify.html",
            "success_url": "/admin/",
            "is_admin": True,
        },
        name="verify",
    ),
    path(
        "manage/",
        staff_member_required(views.passkey_manage),
        {
            "template_name": "maisen_passkeys/manage.html",
            "manage_url_name": "admin_passkeys:manage",
            "is_admin": True,
        },
        name="manage",
    ),
    # JSON-Endpoints (WebAuthn-Zeremonie)
    path(
        "register/begin/",
        staff_member_required(views.passkey_register_begin),
        name="register_begin",
    ),
    path(
        "register/complete/",
        staff_member_required(views.passkey_register_complete),
        name="register_complete",
    ),
    path(
        "authenticate/begin/",
        staff_member_required(views.passkey_authenticate_begin),
        name="authenticate_begin",
    ),
    path(
        "authenticate/complete/",
        staff_member_required(views.passkey_authenticate_complete),
        name="authenticate_complete",
    ),
]

# ---------------------------------------------------------------------------
# Frontend-Passkey-URLs (basic Templates)
# ---------------------------------------------------------------------------
frontend_urlpatterns = [
    path(
        "verify/",
        login_required(views.passkey_verify),
        {
            "template_name": "maisen_passkeys/verify.html",
            "success_url": "/",
        },
        name="verify",
    ),
    path(
        "manage/",
        login_required(views.passkey_manage),
        {
            "template_name": "maisen_passkeys/manage.html",
            "manage_url_name": "passkeys:manage",
        },
        name="manage",
    ),
    # JSON-Endpoints (WebAuthn-Zeremonie)
    path(
        "register/begin/",
        login_required(views.passkey_register_begin),
        name="register_begin",
    ),
    path(
        "register/complete/",
        login_required(views.passkey_register_complete),
        name="register_complete",
    ),
    path(
        "authenticate/begin/",
        login_required(views.passkey_authenticate_begin),
        name="authenticate_begin",
    ),
    path(
        "authenticate/complete/",
        login_required(views.passkey_authenticate_complete),
        name="authenticate_complete",
    ),
]

# Rückwärtskompatibilität: urlpatterns = admin_urlpatterns
urlpatterns = admin_urlpatterns
