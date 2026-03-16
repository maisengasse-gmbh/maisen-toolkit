# Changelog

## v1.0.0 (unreleased)

- Initial release
- TOTP Two-Factor Authentication module
  - TotpUserMixin (abstract model)
  - GroupTotpRequirement model
  - Function-based views (verify, setup, manage)
  - TotpMiddleware (admin + optional frontend)
  - TotpUserAdminMixin
  - TotpCodeForm
  - Base templates (overridable)
  - Configurable via MAISEN_TOTP settings
