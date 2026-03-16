import base64
import io

import pyotp
import qrcode

from maisen.toolkit.conf import get_totp_setting


def render_qr(secret, username):
    """Gibt den QR-Code als base64-encodierten PNG-String zurück."""
    issuer = get_totp_setting("ISSUER")
    uri = pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def user_requires_totp(user):
    """Gibt True zurück, wenn der User TOTP aktivieren muss."""
    if user.is_superuser:
        return True
    return user.groups.filter(totp_requirement__totp_required=True).exists()
