from django.dispatch import Signal

# Gesendet nach erfolgreicher Passkey-Verifikation
# sender=User.__class__, user=user, request=request
passkey_verified = Signal()

# Gesendet nach erfolgreicher Passkey-Registrierung
# sender=User.__class__, user=user, request=request, credential=credential
passkey_registered = Signal()

# Gesendet nach Passkey-Löschung
# sender=User.__class__, user=user, request=request
passkey_deleted = Signal()
