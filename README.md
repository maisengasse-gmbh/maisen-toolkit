# maisen-toolkit

Wiederverwendbares Django-Toolkit von Maisengasse. Stellt gemeinsame Funktionalitaet fuer Django-Projekte als unabhaengige Module bereit.

## Installation

```bash
pip install git+https://github.com/maisengasse-gmbh/maisen-toolkit.git@v0.3.3
```

Mit optionalen Extras:
```bash
pip install "maisen-toolkit[passkeys] @ git+https://github.com/maisengasse-gmbh/maisen-toolkit.git@v0.3.3"
pip install "maisen-toolkit[unfold] @ git+https://github.com/maisengasse-gmbh/maisen-toolkit.git@v0.3.3"
```

Oder in `requirements.txt`:
```
maisen-toolkit[passkeys] @ git+https://github.com/maisengasse-gmbh/maisen-toolkit.git@v0.3.3
```

## Module

| Modul | Beschreibung | Doku |
|---|---|---|
| `maisen.toolkit.core` | TimeStampMixin, DublinCore, Annotation, AddressData, GeoLocation | [README](src/maisen/toolkit/core/README.md) |
| `maisen.toolkit.totp` | TOTP Two-Factor Authentication mit Middleware, Unfold-Support, Signals | [README](src/maisen/toolkit/totp/README.md) |
| `maisen.toolkit.passkeys` | Passkey (WebAuthn) als optionale 2FA-Alternative, fido2-basiert | [README](src/maisen/toolkit/passkeys/README.md) |

## Optionale Dependencies

| Extra | Packages | Beschreibung |
|---|---|---|
| `passkeys` | `fido2>=1.1` | WebAuthn/Passkey-Support |
| `unfold` | `django-unfold` | Admin-UI Styling |
| `dev` | `pytest`, `pytest-django`, `coverage` | Entwicklung |

## Development

```bash
pip install -e ".[dev,passkeys,unfold]"
pytest
```

## Versioning

Git-Tags via setuptools-scm:

```bash
git tag v0.3.3
git push --tags
```
