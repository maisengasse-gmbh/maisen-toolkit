from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class PasskeyUserMixin(models.Model):
    """Abstract Mixin – dem eigenen UserAccount-Model hinzufügen."""

    class Meta:
        abstract = True

    @property
    def has_passkeys(self):
        return self.passkey_credentials.exists()


class PasskeyCredentialMixin(models.Model):
    """Abstract Mixin – dem eigenen Projekt als konkretes Model hinzufügen."""

    class Meta:
        abstract = True
        verbose_name = _("Passkey")
        verbose_name_plural = _("Passkeys")
        ordering = ("-created_at",)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="passkey_credentials",
        verbose_name=_("Benutzer"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_('z.\u202fB. "MacBook Touch ID"'),
    )
    credential_id = models.BinaryField(
        unique=True,
        db_index=True,
        verbose_name=_("Credential-ID"),
    )
    public_key = models.BinaryField(
        verbose_name=_("Public Key"),
    )
    sign_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Sign-Count"),
    )
    aaguid = models.CharField(
        max_length=36,
        blank=True,
        default="",
        verbose_name=_("AAGUID"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Erstellt am"),
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Zuletzt verwendet"),
    )

    def __str__(self):
        return f"{self.name} ({self.user})"
