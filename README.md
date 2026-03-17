# maisen-toolkit

Wiederverwendbares Django-Toolkit von Maisengasse. Stellt gemeinsame Funktionalitaet fuer Django-Projekte als unabhaengige Module bereit.

## Installation

```bash
pip install git+https://github.com/maisengasse-gmbh/maisen-toolkit.git@v0.1.5
```

Oder in `requirements.txt`:
```
maisen-toolkit @ git+https://github.com/maisengasse-gmbh/maisen-toolkit.git@v0.1.5
```

## Module

| Modul | Beschreibung | Doku |
|---|---|---|
| `maisen.toolkit.core` | TimeStampMixin, DublinCore, Annotation, AddressData, GeoLocation | [README](src/maisen/toolkit/core/README.md) |
| `maisen.toolkit.totp` | TOTP Two-Factor Authentication mit Middleware, Unfold-Support, Signals | [README](src/maisen/toolkit/totp/README.md) |

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Versioning

Git-Tags via setuptools-scm:

```bash
git tag v0.1.5
git push --tags
```
