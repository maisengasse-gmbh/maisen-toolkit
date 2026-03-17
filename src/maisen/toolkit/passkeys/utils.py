from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, AttestedCredentialData

from maisen.toolkit.conf import get_passkey_setting


def get_credential_model():
    """Gibt das konfigurierte Passkey-Credential-Model zurück."""
    model_string = get_passkey_setting("CREDENTIAL_MODEL")
    if not model_string:
        raise ImproperlyConfigured(
            "MAISEN_PASSKEYS['CREDENTIAL_MODEL'] muss gesetzt sein, "
            'z.\u202fB. "accounts.PasskeyCredential".'
        )
    return apps.get_model(model_string)


def get_fido2_server():
    """Erstellt einen konfigurierten Fido2Server."""
    rp = PublicKeyCredentialRpEntity(
        id=get_passkey_setting("RP_ID"),
        name=get_passkey_setting("RP_NAME"),
    )
    return Fido2Server(rp)


def user_requires_passkey(user):
    """Gibt True zurück, wenn der User einen Passkey einrichten muss."""
    if user.is_superuser or user.is_staff:
        return True
    return user.groups.filter(passkey_requirement__passkey_required=True).exists()


def get_user_credentials(user):
    """Gibt eine Liste von AttestedCredentialData für den User zurück."""
    CredentialModel = get_credential_model()
    credentials = CredentialModel.objects.filter(user=user)
    result = []
    for cred in credentials:
        result.append(
            AttestedCredentialData.create(
                aaguid=bytes.fromhex(cred.aaguid.replace("-", "")) if cred.aaguid else b"\x00" * 16,
                credential_id=bytes(cred.credential_id),
                public_key=None,  # Not needed for authentication begin
            )
        )
    return result
