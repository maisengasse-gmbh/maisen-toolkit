# maisen-toolkit

Reusable Django toolkit by Maisengasse. Provides common functionality for Django projects.

## Installation

```bash
pip install git+https://github.com/wiegon-gmbh/maisen-toolkit.git@v1.0.0
```

Or in `requirements.txt`:
```
maisen-toolkit @ git+https://github.com/wiegon-gmbh/maisen-toolkit.git@v1.0.0
```

## Modules

### TOTP Two-Factor Authentication

Add `"maisen.toolkit.totp"` to `INSTALLED_APPS` and configure:

```python
INSTALLED_APPS = [
    ...
    "maisen.toolkit.totp",
]

MAISEN_TOTP = {
    "ISSUER": "My App",                       # Name in Authenticator-App
    "VERIFY_VALID_WINDOW": 1,                 # Toleranz bei Verifikation (Default: 1)
    "SETUP_VALID_WINDOW": 2,                  # Toleranz bei Setup (Default: 2)
    "ADMIN_ONLY": True,                       # Nur Admin schuetzen (Default: True)
    "EXEMPT_URL_PREFIXES": (                  # Frontend-Ausnahmen (wenn ADMIN_ONLY=False)
        "/login/", "/logout/", "/static/",
    ),
}
```

Add the mixin to your user model:

```python
from maisen.toolkit.totp.models import TotpUserMixin

class UserAccount(AbstractUser, TotpUserMixin):
    ...
```

Add middleware:

```python
MIDDLEWARE = [
    ...
    "maisen.toolkit.totp.middleware.TotpMiddleware",
]
```

Add URLs (using default templates or your own):

```python
from maisen.toolkit.totp import urls as totp_urls

urlpatterns = [
    path("admin/totp/", include((totp_urls, "totp"), namespace="totp")),
    path("admin/", admin.site.urls),
]
```

For custom templates, define your own URL patterns:

```python
from django.contrib.admin.views.decorators import staff_member_required
from maisen.toolkit.totp import views as totp_views

urlpatterns = [
    path(
        "admin/totp/verify/",
        staff_member_required(totp_views.totp_verify),
        {"template_name": "my_app/totp_verify.html", "is_admin": True},
        name="verify",
    ),
    ...
]
```

Admin integration:

```python
from maisen.toolkit.totp.admin import TotpUserAdminMixin

class AccountAdmin(TotpUserAdminMixin, UserAdmin):
    fieldsets = UserAdmin.fieldsets + TotpUserAdminMixin.totp_fieldset
    readonly_fields = TotpUserAdminMixin.totp_readonly_fields
    actions = ["reset_totp"]
```

Run migration:

```bash
python manage.py migrate maisen_totp
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Versioning

Uses setuptools-scm. Version is derived from git tags:

```bash
git tag v1.0.0
git push --tags
```
