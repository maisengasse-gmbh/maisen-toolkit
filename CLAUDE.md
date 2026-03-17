# CLAUDE.md – maisen-toolkit

## Projekt

Wiederverwendbares Django-Toolkit von Maisengasse. Aktuell ein Modul: **TOTP Two-Factor Authentication**.

- **Django 4.2+**, Python 3.9+
- **Optionale Abhängigkeit**: django-unfold (Unfold-Admin-Templates + Form)
- **Package-Format**: Namespace-Package `maisen.toolkit`

## Entwicklungsumgebung

```bash
pip install -e ".[dev]"
pytest
```

## Code-Style

- **Black** (line-length=88), **Ruff**
- Doppelte Anführungszeichen für Strings

## Projektstruktur

```
src/maisen/toolkit/
├── conf.py                    # Settings (MAISEN_TOTP Defaults + get_totp_setting)
└── totp/                      # TOTP-Modul
    ├── apps.py                # TotpConfig (label="maisen_totp")
    ├── models.py              # TotpUserMixin, GroupTotpRequirementMixin (beide abstract)
    ├── forms.py               # TotpCodeForm, UnfoldTotpCodeForm (try/except)
    ├── views.py               # totp_verify, totp_setup, totp_manage (FBVs)
    ├── middleware.py           # TotpMiddleware (reverse()-basiert)
    ├── decorators.py           # @totp_required
    ├── signals.py              # totp_verified, totp_setup_complete, totp_disabled
    ├── utils.py               # render_qr, user_requires_totp
    ├── admin.py               # TotpUserAdminMixin
    ├── urls.py                # admin_urlpatterns + frontend_urlpatterns (basic)
    ├── urls_unfold.py         # admin_urlpatterns (Unfold-Templates + Form)
    ├── migrations/
    └── templates/maisen_totp/
        ├── verify.html, setup.html, manage.html        # Basic
        └── unfold/verify.html, setup.html, manage.html # Unfold
```

## Konventionen

### Views: Function-Based, parametrisiert
Alle Views sind FBVs mit konfigurierbaren Parametern (template_name, form_class, success_url, is_admin). Kein Class-Based.

### Models: Nur Abstract Mixins
Das Toolkit definiert KEINE konkreten Models. Projekte erstellen eigene konkrete Models, die von den Mixins erben.

### Settings: MAISEN_TOTP Dict
Konfiguration via `MAISEN_TOTP` in Django-Settings. `conf.py:get_totp_setting()` liest mit Defaults.

### Templates: Namespaced unter maisen_totp/
Basic-Varianten als Fallback, Unfold-Varianten für django-unfold Admin.

### URLs: Include-bar
Projekte importieren `admin_urlpatterns`/`frontend_urlpatterns` und binden sie per `include()` ein.

### Middleware: reverse()-basiert
URL-Namen konfigurierbar via Settings (ADMIN_VERIFY_URL_NAME, etc.). Keine hardcoded Pfade.

## Git-Commits

```
feat: Kurzbeschreibung
fix: Kurzbeschreibung
refactor: Kurzbeschreibung
```

## Versionierung

Git-Tags: `v0.1.x`. Version via setuptools-scm.
