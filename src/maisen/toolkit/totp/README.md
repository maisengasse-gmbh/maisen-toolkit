# maisen.toolkit.totp — TOTP Two-Factor Authentication

TOTP-basierte Zwei-Faktor-Authentifizierung fuer Django. Unterstuetzt Django Admin (mit optionalem Unfold-Styling) und Frontend.

## Features

- Abstract Model Mixins (`TotpUserMixin`, `GroupTotpRequirementMixin`)
- Konfigurierbare Middleware mit `reverse()`-basierten Redirects
- Fertige URL-Patterns fuer Admin + Frontend (basic und Unfold)
- `@totp_required` Decorator als Alternative zur Middleware
- Signals (`totp_verified`, `totp_setup_complete`, `totp_disabled`)
- Admin-Mixin fuer User-Admin mit TOTP-Fieldset und Reset-Action

## Quick Start

### 1. INSTALLED_APPS

```python
INSTALLED_APPS = [
    ...
    "maisen.toolkit.totp",
]
```

### 2. User-Model

```python
from maisen.toolkit.totp.models import TotpUserMixin

class UserAccount(AbstractUser, TotpUserMixin):
    ...
```

Optional fuer gruppenbasierte TOTP-Pflicht:

```python
from maisen.toolkit.totp.models import GroupTotpRequirementMixin

class GroupTotpRequirement(GroupTotpRequirementMixin):
    pass
```

### 3. Migration

```bash
python manage.py migrate maisen_totp
```

### 4. URLs

**Fuer Unfold-Admin + Frontend:**

```python
from maisen.toolkit.totp.urls_unfold import admin_urlpatterns as totp_admin
from maisen.toolkit.totp.urls import frontend_urlpatterns as totp_frontend

urlpatterns = [
    path("admin/totp/", include((totp_admin, "totp"), namespace="admin_totp")),
    path("totp/", include((totp_frontend, "totp"), namespace="totp")),
    path("admin/", admin.site.urls),
]
```

**Fuer Standard-Admin:**

```python
from maisen.toolkit.totp.urls import admin_urlpatterns as totp_admin

urlpatterns = [
    path("admin/totp/", include((totp_admin, "totp"), namespace="admin_totp")),
    path("admin/", admin.site.urls),
]
```

**Eigene Patterns (volle Kontrolle):**

```python
from maisen.toolkit.totp import views as totp_views

urlpatterns = [
    path("admin/totp/verify/",
         staff_member_required(totp_views.totp_verify),
         {"template_name": "my/verify.html", "is_admin": True, "success_url": "/admin/"},
         name="verify"),
    ...
]
```

### 5. Middleware

```python
MIDDLEWARE = [
    ...
    "maisen.toolkit.totp.middleware.TotpMiddleware",
]
```

### 6. Admin-Integration

```python
from maisen.toolkit.totp.admin import TotpUserAdminMixin

class AccountAdmin(TotpUserAdminMixin, UserAdmin):
    fieldsets = UserAdmin.fieldsets + TotpUserAdminMixin.totp_fieldset
    readonly_fields = TotpUserAdminMixin.totp_readonly_fields
    actions = ["reset_totp"]
```

## Settings

Alle Settings werden ueber das `MAISEN_TOTP` Dict in den Django-Settings konfiguriert:

```python
MAISEN_TOTP = {
    # Allgemein
    "ISSUER": "My App",              # Name in Authenticator-App (Default: "Django App")
    "VERIFY_VALID_WINDOW": 1,        # Toleranz bei Verifikation (Default: 1)
    "SETUP_VALID_WINDOW": 2,         # Toleranz bei Setup (Default: 2)

    # Middleware
    "ADMIN_ONLY": True,              # Nur Admin schuetzen (Default: True)

    # URL-Namen fuer Middleware-Redirects
    "ADMIN_VERIFY_URL_NAME": "admin_totp:verify",
    "ADMIN_SETUP_URL_NAME": "admin_totp:setup",
    "ADMIN_MANAGE_URL_NAME": "admin_totp:manage",
    "FRONTEND_VERIFY_URL_NAME": "totp:verify",
    "FRONTEND_SETUP_URL_NAME": "totp:setup",

    # Exempt-Pfade
    "ADMIN_EXEMPT_PREFIXES": ("/admin/login", "/admin/logout", "/admin/jsi18n"),
    "EXEMPT_URL_PREFIXES": ("/login/", "/logout/", "/static/", "/media/", "/api/"),
}
```

## Decorator

Alternative zur Middleware fuer per-View Enforcement:

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

## Signals

```python
from django.dispatch import receiver
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

## Templates

Das Modul liefert zwei Template-Sets unter `maisen_totp/`:

| Pfad | Verwendung |
|---|---|
| `maisen_totp/verify.html` | Basic Admin/Frontend |
| `maisen_totp/setup.html` | Basic Admin/Frontend |
| `maisen_totp/manage.html` | Basic Admin/Frontend |
| `maisen_totp/unfold/verify.html` | Unfold-Admin |
| `maisen_totp/unfold/setup.html` | Unfold-Admin |
| `maisen_totp/unfold/manage.html` | Unfold-Admin |

Eigene Templates koennen per `template_name` in den URL-Patterns oder per Django Template-Overriding verwendet werden.
