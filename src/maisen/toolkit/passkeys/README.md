# maisen.toolkit.passkeys — Passkey (WebAuthn) Authentication

Optionale Passkey/WebAuthn-Authentifizierung fuer Django. Passkeys sind immer eine **Alternative** zu TOTP, nie Pflicht. Unterstuetzt Django Admin (mit optionalem Unfold-Styling) und Frontend.

## Features

- Abstract Model Mixins (`PasskeyUserMixin`, `PasskeyCredentialMixin`)
- WebAuthn-Zeremonie (Register + Authenticate) via JSON-Endpoints
- Fertige URL-Patterns fuer Admin + Frontend (basic und Unfold)
- Integration mit TOTP-Middleware (`ACCEPT_PASSKEY_VERIFIED`)
- Signals (`passkey_verified`, `passkey_registered`, `passkey_deleted`)
- Admin-Mixin fuer User-Admin mit Passkey-Fieldset und Reset-Action
- JavaScript-Helper (`webauthn.js`) fuer Browser-API

## Dependency

```bash
pip install maisen-toolkit[passkeys]   # installiert fido2>=1.1
```

## Quick Start

### 1. INSTALLED_APPS

```python
INSTALLED_APPS = [
    ...
    "maisen.toolkit.totp",       # TOTP bleibt Primary 2FA
    "maisen.toolkit.passkeys",
]
```

### 2. User-Model

```python
from maisen.toolkit.totp.models import TotpUserMixin
from maisen.toolkit.passkeys.models import PasskeyCredentialMixin, PasskeyUserMixin

class UserAccount(AbstractUser, TotpUserMixin, PasskeyUserMixin):
    ...

class PasskeyCredential(PasskeyCredentialMixin):
    pass
```

### 3. Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Settings

```python
MAISEN_TOTP = {
    "ISSUER": "My App",
    "ACCEPT_PASSKEY_VERIFIED": True,   # TOTP-Middleware akzeptiert Passkeys
    "ADMIN_EXEMPT_PREFIXES": (
        "/admin/login", "/admin/logout", "/admin/jsi18n",
        "/admin/passkeys/",            # Passkey-URLs exempt
    ),
}

MAISEN_PASSKEYS = {
    "RP_ID": "localhost",              # Domain (Produktion: "example.com")
    "RP_NAME": "My App",              # Anzeigename
    "ORIGIN": "http://localhost:8000", # Origin fuer WebAuthn
    "CREDENTIAL_MODEL": "accounts.PasskeyCredential",  # Pflicht!
}
```

### 5. URLs

**Fuer Unfold-Admin:**

```python
from maisen.toolkit.passkeys.urls_unfold import admin_urlpatterns as passkey_admin

urlpatterns = [
    path("admin/passkeys/", include((passkey_admin, "passkeys"), namespace="admin_passkeys")),
    path("admin/", admin.site.urls),
]
```

**Fuer Admin + Frontend:**

```python
from maisen.toolkit.passkeys.urls_unfold import admin_urlpatterns as passkey_admin
from maisen.toolkit.passkeys.urls import frontend_urlpatterns as passkey_frontend

urlpatterns = [
    path("admin/passkeys/", include((passkey_admin, "passkeys"), namespace="admin_passkeys")),
    path("passkeys/", include((passkey_frontend, "passkeys"), namespace="passkeys")),
    path("admin/", admin.site.urls),
]
```

### 6. Admin-Integration

```python
from maisen.toolkit.totp.admin import TotpUserAdminMixin
from maisen.toolkit.passkeys.admin import PasskeyUserAdminMixin

class AccountAdmin(TotpUserAdminMixin, PasskeyUserAdminMixin, UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        TotpUserAdminMixin.totp_fieldset
        + PasskeyUserAdminMixin.passkey_fieldset
    )
    readonly_fields = (
        TotpUserAdminMixin.totp_readonly_fields
        + PasskeyUserAdminMixin.passkey_readonly_fields
    )
    actions = ["reset_totp", "reset_passkeys"]
```

## Architektur

Passkeys sind **immer optional** — es gibt keine Middleware und keinen Decorator, der Passkeys erzwingt. Stattdessen:

1. **TOTP bleibt Primary 2FA** mit Pflicht-Durchsetzung via `TotpMiddleware`
2. **Passkeys als Alternative**: Wenn `ACCEPT_PASSKEY_VERIFIED: True`, akzeptiert die TOTP-Middleware `session["passkey_verified"]` als gueltige Verifikation
3. **TOTP-Verify-Template** zeigt automatisch einen "Mit Passkey verifizieren"-Button, wenn der User Passkeys registriert hat
4. **Kein TOTP-Setup-Zwang**: Wenn ein User Passkeys hat aber kein TOTP, wird er zur Verify-Seite geleitet (nicht zum TOTP-Setup)

## URL-Endpoints

| Pfad | Methode | Beschreibung |
|---|---|---|
| `verify/` | GET | Passkey-Verify-Seite |
| `manage/` | GET/POST | Passkeys verwalten (Liste, Loeschen) |
| `register/begin/` | POST | Registrierung starten (JSON) |
| `register/complete/` | POST | Registrierung abschliessen (JSON) |
| `authenticate/begin/` | POST | Authentifizierung starten (JSON) |
| `authenticate/complete/` | POST | Authentifizierung abschliessen (JSON) |

## Signals

```python
from maisen.toolkit.passkeys.signals import passkey_verified, passkey_registered, passkey_deleted

@receiver(passkey_verified)
def on_passkey_verified(sender, user, request, **kwargs):
    logger.info(f"Passkey verified for {user.username}")

@receiver(passkey_registered)
def on_passkey_registered(sender, user, request, credential, **kwargs):
    logger.info(f"Passkey registered: {credential.name}")

@receiver(passkey_deleted)
def on_passkey_deleted(sender, user, request, **kwargs):
    logger.info(f"Passkey deleted for {user.username}")
```

## Templates

| Pfad | Verwendung |
|---|---|
| `maisen_passkeys/verify.html` | Basic Admin/Frontend |
| `maisen_passkeys/manage.html` | Basic Admin/Frontend |
| `maisen_passkeys/unfold/verify.html` | Unfold-Admin |
| `maisen_passkeys/unfold/manage.html` | Unfold-Admin |

## Static Files

`maisen_passkeys/js/webauthn.js` — JavaScript-Helper mit:
- `registerPasskey(beginUrl, completeUrl, csrfToken, name)` — Passkey registrieren
- `authenticatePasskey(beginUrl, completeUrl, csrfToken)` — Mit Passkey verifizieren

## Kompatibilitaet

- Python >= 3.9
- Django >= 4.2
- fido2 >= 1.1 (getestet mit 2.1)
- Optional: django-unfold (fuer Admin-Styling)
