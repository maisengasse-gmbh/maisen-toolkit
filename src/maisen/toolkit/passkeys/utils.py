from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from fido2 import cbor
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


def get_user_credentials(user):
    """Gibt eine Liste von AttestedCredentialData für den User zurück."""
    CredentialModel = get_credential_model()
    credentials = CredentialModel.objects.filter(user=user)
    result = []
    for cred in credentials:
        public_key = cbor.decode(bytes(cred.public_key))
        result.append(
            AttestedCredentialData.create(
                aaguid=bytes.fromhex(cred.aaguid.replace("-", "")) if cred.aaguid else b"\x00" * 16,
                credential_id=bytes(cred.credential_id),
                public_key=public_key,
            )
        )
    return result
