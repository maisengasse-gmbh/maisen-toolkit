# maisen-toolkit

Reusable Django toolkit by Maisengasse. Provides common functionality for Django projects.

## Installation

```bash
pip install git+https://github.com/maisengasse-gmbh/maisen-toolkit.git@v0.1.5
```

Or in `requirements.txt`:
```
maisen-toolkit @ git+https://github.com/maisengasse-gmbh/maisen-toolkit.git@v0.1.5
```

## TOTP Two-Factor Authentication

### 1. INSTALLED_APPS und Settings

```python
INSTALLED_APPS = [
    ...
    "maisen.toolkit.totp",
]

MAISEN_TOTP = {
    "ISSUER": "My App",                        # Name in Authenticator-App
    "VERIFY_VALID_WINDOW": 1,                  # Toleranz bei Verifikation (Default: 1)
    "SETUP_VALID_WINDOW": 2,                   # Toleranz bei Setup (Default: 2)
    "ADMIN_ONLY": True,                        # Nur Admin schuetzen (Default: True)
    # URL-Namen fuer Middleware-Redirects (muessen zu den URL-Patterns passen)
    "ADMIN_VERIFY_URL_NAME": "admin_totp:verify",   # Default
    "ADMIN_SETUP_URL_NAME": "admin_totp:setup",     # Default
    "ADMIN_MANAGE_URL_NAME": "admin_totp:manage",   # Default
    "FRONTEND_VERIFY_URL_NAME": "totp:verify",      # Default
    "FRONTEND_SETUP_URL_NAME": "totp:setup",        # Default
    # Admin-Pfade ohne TOTP-Schutz
    "ADMIN_EXEMPT_PREFIXES": ("/admin/login", "/admin/logout", "/admin/jsi18n"),
    # Frontend-Ausnahmen (wenn ADMIN_ONLY=False)
    "EXEMPT_URL_PREFIXES": ("/login/", "/logout/", "/static/", "/media/", "/api/"),
}
```

### 2. User-Model

```python
from maisen.toolkit.totp.models import TotpUserMixin

class UserAccount(AbstractUser, TotpUserMixin):
    ...
```

Optional GroupTotpRequirement:
```python
from maisen.toolkit.totp.models import GroupTotpRequirementMixin

class GroupTotpRequirement(GroupTotpRequirementMixin):
    pass
```

### 3. Middleware

```python
MIDDLEWARE = [
    ...
    "maisen.toolkit.totp.middleware.TotpMiddleware",
]
```

### 4. URLs

**Option A: Fertige Patterns (empfohlen)**

Fuer Unfold-Admin:
```python
from maisen.toolkit.totp.urls_unfold import admin_urlpatterns as totp_admin
from maisen.toolkit.totp.urls import frontend_urlpatterns as totp_frontend

urlpatterns = [
    path("admin/totp/", include((totp_admin, "totp"), namespace="admin_totp")),
    path("totp/", include((totp_frontend, "totp"), namespace="totp")),
    path("admin/", admin.site.urls),
]
```

Fuer Standard-Admin:
```python
from maisen.toolkit.totp.urls import admin_urlpatterns as totp_admin

urlpatterns = [
    path("admin/totp/", include((totp_admin, "totp"), namespace="admin_totp")),
    path("admin/", admin.site.urls),
]
```

**Option B: Eigene Patterns**

```python
from maisen.toolkit.totp import views as totp_views

urlpatterns = [
    path("admin/totp/verify/",
         staff_member_required(totp_views.totp_verify),
         {"template_name": "my_app/verify.html", "is_admin": True, "success_url": "/admin/"},
         name="verify"),
    ...
]
```

### 5. Admin-Integration

```python
from maisen.toolkit.totp.admin import TotpUserAdminMixin

class AccountAdmin(TotpUserAdminMixin, UserAdmin):
    fieldsets = UserAdmin.fieldsets + TotpUserAdminMixin.totp_fieldset
    readonly_fields = TotpUserAdminMixin.totp_readonly_fields
    actions = ["reset_totp"]
```

### 6. Decorator (Alternative zur Middleware)

```python
from maisen.toolkit.totp.decorators import totp_required

@login_required
@totp_required
def my_view(request):
    ...

@login_required
@totp_required(verify_url_name="admin_totp:verify")
def my_admin_view(request):
    ...
```

### 7. Signals

```python
from maisen.toolkit.totp.signals import totp_verified, totp_setup_complete, totp_disabled

@receiver(totp_verified)
def on_totp_verified(sender, user, request, **kwargs):
    logger.info(f"TOTP verified for {user.username}")

@receiver(totp_setup_complete)
def on_totp_setup(sender, user, request, **kwargs):
    logger.info(f"TOTP setup complete for {user.username}")

@receiver(totp_disabled)
def on_totp_disabled(sender, user, request, **kwargs):
    logger.info(f"TOTP disabled for {user.username}")
```

### 8. Migration

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
git tag v0.1.5
git push --tags
```
