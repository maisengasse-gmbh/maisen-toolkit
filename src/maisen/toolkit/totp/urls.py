"""
Standard-URL-Patterns für Admin-TOTP.

Verwendung in urls.py des Projekts:

    from maisen.toolkit.totp import urls as totp_urls

    urlpatterns = [
        path("admin/totp/", include((totp_urls, "totp"), namespace="totp")),
        ...
    ]

Für eigene Templates und Decorators die Patterns im Projekt definieren
und die Views direkt importieren.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from maisen.toolkit.totp import views

app_name = "totp"

urlpatterns = [
    path(
        "verify/",
        staff_member_required(views.totp_verify),
        {"template_name": "maisen_totp/verify.html", "success_url": "/admin/", "is_admin": True},
        name="verify",
    ),
    path(
        "setup/",
        staff_member_required(views.totp_setup),
        {"template_name": "maisen_totp/setup.html", "is_admin": True},
        name="setup",
    ),
    path(
        "manage/",
        staff_member_required(views.totp_manage),
        {"template_name": "maisen_totp/manage.html", "is_admin": True},
        name="manage",
    ),
]
