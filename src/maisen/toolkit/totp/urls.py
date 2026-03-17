"""
Standard-URL-Patterns für TOTP (Admin + Frontend).

Verwendung in urls.py des Projekts:

    from maisen.toolkit.totp.urls import admin_urlpatterns, frontend_urlpatterns

    urlpatterns = [
        path("admin/totp/", include((admin_urlpatterns, "totp"), namespace="admin_totp")),
        path("totp/", include((frontend_urlpatterns, "totp"), namespace="totp")),
        ...
    ]

Für Unfold-Admin-Templates stattdessen urls_unfold verwenden:

    from maisen.toolkit.totp.urls_unfold import admin_urlpatterns
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.urls import path

from maisen.toolkit.totp import views

app_name = "totp"

# ---------------------------------------------------------------------------
# Admin-TOTP-URLs (basic Templates)
# ---------------------------------------------------------------------------
admin_urlpatterns = [
    path(
        "verify/",
        staff_member_required(views.totp_verify),
        {
            "template_name": "maisen_totp/verify.html",
            "success_url": "/admin/",
            "setup_url_name": "admin_totp:setup",
            "is_admin": True,
        },
        name="verify",
    ),
    path(
        "setup/",
        staff_member_required(views.totp_setup),
        {
            "template_name": "maisen_totp/setup.html",
            "manage_url_name": "admin_totp:manage",
            "is_admin": True,
        },
        name="setup",
    ),
    path(
        "manage/",
        staff_member_required(views.totp_manage),
        {
            "template_name": "maisen_totp/manage.html",
            "manage_url_name": "admin_totp:manage",
            "setup_url_name": "admin_totp:setup",
            "is_admin": True,
        },
        name="manage",
    ),
]

# ---------------------------------------------------------------------------
# Frontend-TOTP-URLs (basic Templates)
# ---------------------------------------------------------------------------
frontend_urlpatterns = [
    path(
        "verify/",
        login_required(views.totp_verify),
        {
            "template_name": "maisen_totp/verify.html",
            "success_url": "/",
            "setup_url_name": "totp:setup",
        },
        name="verify",
    ),
    path(
        "setup/",
        login_required(views.totp_setup),
        {
            "template_name": "maisen_totp/setup.html",
            "manage_url_name": "totp:manage",
        },
        name="setup",
    ),
    path(
        "manage/",
        login_required(views.totp_manage),
        {
            "template_name": "maisen_totp/manage.html",
            "manage_url_name": "totp:manage",
            "setup_url_name": "totp:setup",
        },
        name="manage",
    ),
]

# Rückwärtskompatibilität: urlpatterns = admin_urlpatterns
urlpatterns = admin_urlpatterns
