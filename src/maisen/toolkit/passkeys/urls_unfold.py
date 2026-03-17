"""
Unfold-Admin-URL-Patterns für Passkeys.

Verwendung in urls.py des Projekts:

    from maisen.toolkit.passkeys.urls_unfold import admin_urlpatterns

    urlpatterns = [
        path("admin/passkeys/", include((admin_urlpatterns, "passkeys"), namespace="admin_passkeys")),
        ...
    ]
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from maisen.toolkit.passkeys import views
from maisen.toolkit.passkeys.forms import UnfoldPasskeyNameForm

admin_urlpatterns = [
    path(
        "verify/",
        staff_member_required(views.passkey_verify),
        {
            "template_name": "maisen_passkeys/unfold/verify.html",
            "success_url": "/admin/",
            "is_admin": True,
        },
        name="verify",
    ),
    path(
        "manage/",
        staff_member_required(views.passkey_manage),
        {
            "template_name": "maisen_passkeys/unfold/manage.html",
            "manage_url_name": "admin_passkeys:manage",
            "is_admin": True,
            "form_class": UnfoldPasskeyNameForm,
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
