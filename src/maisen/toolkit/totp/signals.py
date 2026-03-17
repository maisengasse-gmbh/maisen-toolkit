from django.dispatch import Signal

# Gesendet nach erfolgreicher TOTP-Verifikation
# sender=User.__class__, user=user, request=request
totp_verified = Signal()

# Gesendet nach erfolgreichem TOTP-Setup
# sender=User.__class__, user=user, request=request
totp_setup_complete = Signal()

# Gesendet nach TOTP-Deaktivierung
# sender=User.__class__, user=user, request=request
totp_disabled = Signal()
