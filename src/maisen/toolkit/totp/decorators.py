from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse

from maisen.toolkit.conf import get_totp_setting
from maisen.toolkit.totp.utils import user_requires_totp


def totp_required(view_func=None, verify_url_name=None):
    """
    Per-View TOTP-Enforcement als Alternative zur Middleware.

    Verwendung:
        @login_required
        @totp_required
        def my_view(request):
            ...

        @login_required
        @totp_required(verify_url_name="admin_totp:verify")
        def my_admin_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            if not user_requires_totp(request.user):
                return view_func(request, *args, **kwargs)
            if request.session.get("totp_verified"):
                return view_func(request, *args, **kwargs)
            url_name = verify_url_name or get_totp_setting(
                "FRONTEND_VERIFY_URL_NAME"
            )
            return redirect(reverse(url_name))

        return _wrapped

    if view_func:
        return decorator(view_func)
    return decorator
