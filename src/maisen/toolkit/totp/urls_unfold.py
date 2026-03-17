"""
Unfold-Admin-URL-Patterns für TOTP.

Verwendung in urls.py des Projekts:

    from maisen.toolkit.totp.urls_unfold import admin_urlpatterns

    urlpatterns = [
        path("admin/totp/", include((admin_urlpatterns, "totp"), namespace="admin_totp")),
        ...
    ]
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from maisen.toolkit.totp import views
from maisen.toolkit.totp.forms import UnfoldTotpCodeForm

admin_urlpatterns = [
    path(
        "verify/",
        staff_member_required(views.totp_verify),
        {
            "template_name": "maisen_totp/unfold/verify.html",
            "success_url": "/admin/",
            "setup_url_name": "admin_totp:setup",
            "is_admin": True,
            "form_class": UnfoldTotpCodeForm,
        },
        name="verify",
    ),
    path(
        "setup/",
        staff_member_required(views.totp_setup),
        {
            "template_name": "maisen_totp/unfold/setup.html",
            "manage_url_name": "admin_totp:manage",
            "is_admin": True,
            "form_class": UnfoldTotpCodeForm,
        },
        name="setup",
    ),
    path(
        "manage/",
        staff_member_required(views.totp_manage),
        {
            "template_name": "maisen_totp/unfold/manage.html",
            "manage_url_name": "admin_totp:manage",
            "setup_url_name": "admin_totp:setup",
            "is_admin": True,
            "form_class": UnfoldTotpCodeForm,
        },
        name="manage",
    ),
]
